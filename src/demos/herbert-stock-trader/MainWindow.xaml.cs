using System.Diagnostics;
using System.Text;
using System.Text.Json;
using Microsoft.UI.Dispatching;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using HerbertStockTrader.Services;

namespace HerbertStockTrader;

public sealed partial class MainWindow : Window
{
    private ContainerService? _containerService;
    private DispatcherQueue? _dispatcherQueue;
    private DispatcherTimer? _fileRefreshTimer;
    private DispatcherTimer? _wsRetryTimer;

    // WebSocket
    private System.Net.WebSockets.ClientWebSocket? _webSocket;
    private volatile bool _wsConnected;
    private int _wsRetryCount;
    private CancellationTokenSource? _wsCts;

    // Log display
    private readonly StringBuilder _logBuffer = new();
    private readonly object _logLock = new();
    private readonly StringBuilder _pendingOutput = new();
    private const int MaxLogChars = 50_000;

    // File tree: display text → full path
    private readonly Dictionary<string, string> _nodePathMap = new();

    // Desktop WebView state
    private WebView2? _desktopWebView;
    private bool _desktopInitialized;
    private bool _desktopInitInProgress;

    private bool _closed;
    private bool _dashboardActive = true;
    private bool _suppressContainerOutput;

    private static readonly string HerbertFolder = @"C:\temp\Herbert\Documents";
    private static readonly HashSet<string> HiddenFiles = new(StringComparer.OrdinalIgnoreCase)
    {
        "debug.log", "app_startup.log", "trades.csv"
    };

    public MainWindow()
    {
        InitializeComponent();
        Closed += OnClosed;
    }

    private void OnLoaded(object sender, RoutedEventArgs e)
    {
        Debug.WriteLine("[MainWindow] OnLoaded entered");
        try
        {
            Title = "Herbert Stock Trader";
            ExtendsContentIntoTitleBar = true;

            _dispatcherQueue = DispatcherQueue.GetForCurrentThread();

            NavView.SelectedItem = DashboardNavItem;

            // File browser refresh timer (every 5 seconds)
            _fileRefreshTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(5) };
            _fileRefreshTimer.Tick += (_, _) =>
            {
                if (_dashboardActive) RefreshFileTree();
            };
            _fileRefreshTimer.Start();
            RefreshFileTree();

            // Wire up file tree item click handler
            FileTreeView.ItemInvoked += OnFileInvoked;

            StartContainerAsync();
            Debug.WriteLine("[MainWindow] OnLoaded done");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[MainWindow] OnLoaded EXCEPTION: 0x{ex.HResult:X8} {ex.Message}");
        }
    }

    // ========== Navigation ==========

    private void NavView_SelectionChanged(NavigationView sender,
        NavigationViewSelectionChangedEventArgs args)
    {
        if (_closed) return;

        try
        {
            if (args.IsSettingsSelected) return;

            var selectedItem = args.SelectedItemContainer;
            if (selectedItem is not NavigationViewItem navItem) return;

            var tag = navItem.Tag?.ToString();
            if (tag == "Dashboard")
            {
                DashboardPanel.Visibility = Visibility.Visible;
                DesktopPanel.Visibility = Visibility.Collapsed;
                _dashboardActive = true;
                RefreshFileTree();
            }
            else if (tag == "Herbert")
            {
                DashboardPanel.Visibility = Visibility.Collapsed;
                DesktopPanel.Visibility = Visibility.Visible;
                _dashboardActive = false;

                if (!_desktopInitialized && !_desktopInitInProgress)
                    _ = InitDesktopWebViewAsync();
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[MainWindow] NavView_SelectionChanged exception: {ex.Message}");
        }
    }

    // ========== Desktop WebView ==========

    private async Task InitDesktopWebViewAsync()
    {
        _desktopInitInProgress = true;
        Debug.WriteLine("[MainWindow] Initializing WebView2 for noVNC...");

        try
        {
            _desktopWebView = new WebView2
            {
                HorizontalAlignment = HorizontalAlignment.Stretch,
                VerticalAlignment = VerticalAlignment.Stretch
            };
            Grid.SetRow(_desktopWebView, 0);
            DesktopPanel.Children.Insert(0, _desktopWebView);

            await _desktopWebView.EnsureCoreWebView2Async();

            if (_closed) return;

            _desktopWebView.NavigationCompleted += OnDesktopNavigationCompleted;
            _desktopWebView.Source = new Uri("http://localhost:6080/vnc.html?autoconnect=true&resize=scale&scaleViewport=true&clipViewport=false");
            _desktopInitialized = true;
            Debug.WriteLine("[MainWindow] WebView2 navigated to noVNC");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[MainWindow] WebView2 init error: 0x{ex.HResult:X8} {ex.Message}");
        }
        finally
        {
            _desktopInitInProgress = false;
        }
    }

    private async void OnDesktopNavigationCompleted(WebView2 sender,
        Microsoft.Web.WebView2.Core.CoreWebView2NavigationCompletedEventArgs args)
    {
        if (!args.IsSuccess || _closed) return;

        // Inject JS to force noVNC to scale the viewport and hide the control bar
        try
        {
            await sender.ExecuteScriptAsync(@"
                (function() {
                    // Hide the noVNC control bar for a cleaner embedded look
                    var controlBar = document.getElementById('noVNC_control_bar_anchor');
                    if (controlBar) controlBar.style.display = 'none';

                    // Poll until the RFB connection object is available
                    function configureScaling() {
                        var ui = window.UI;
                        if (ui && ui.rfb) {
                            ui.rfb.scaleViewport = true;
                            ui.rfb.clipViewport = false;
                            ui.rfb.resizeSession = false;
                            return;
                        }
                        // Fallback: check for global rfb
                        if (window.rfb) {
                            window.rfb.scaleViewport = true;
                            window.rfb.clipViewport = false;
                            window.rfb.resizeSession = false;
                            return;
                        }
                        setTimeout(configureScaling, 300);
                    }
                    configureScaling();

                    // Also ensure the container fills the viewport
                    var style = document.createElement('style');
                    style.textContent = `
                        html, body { margin: 0; padding: 0; overflow: hidden; }
                        #noVNC_container { width: 100vw !important; height: 100vh !important; }
                    `;
                    document.head.appendChild(style);
                })();
            ");
            Debug.WriteLine("[MainWindow] Injected noVNC scaling script");
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[MainWindow] Script injection error: {ex.Message}");
        }
    }

    // ========== Desktop Commands ==========

    private async void GoBackToWorkButton_Click(object sender, RoutedEventArgs e)
    {
        try
        {
            if (_webSocket?.State == System.Net.WebSockets.WebSocketState.Open)
            {
                var msg = Encoding.UTF8.GetBytes("{\"type\":\"command\",\"action\":\"go_back_to_work\"}");
                await _webSocket.SendAsync(
                    msg,
                    System.Net.WebSockets.WebSocketMessageType.Text,
                    endOfMessage: true,
                    CancellationToken.None);
                Debug.WriteLine("[MainWindow] Sent go_back_to_work command");
            }
            else
            {
                Debug.WriteLine("[MainWindow] WebSocket not connected, cannot send command");
            }
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[MainWindow] GoBackToWork send error: {ex.Message}");
        }
    }

    // ========== Window Close ==========

    private void OnClosed(object sender, WindowEventArgs args)
    {
        _closed = true;

        _fileRefreshTimer?.Stop();
        _wsRetryTimer?.Stop();
        _wsCts?.Cancel();

        try { _webSocket?.Dispose(); }
        catch { /* ignore */ }
        _webSocket = null;

        if (_containerService != null)
        {
            var svc = _containerService;
            _containerService = null;
            Task.Run(() => svc.Shutdown());
        }
    }

    // ========== Container Management ==========

    private void StartContainerAsync()
    {
        _containerService = new ContainerService();

        _containerService.OutputReceived += text => OnContainerOutput(text);
        _containerService.StatusChanged += text => OnContainerStatus(text);

        var svc = _containerService;
        Task.Run(() =>
        {
            try
            {
                svc.StartContainer();

                if (_dispatcherQueue != null && !_closed)
                {
                    _dispatcherQueue.TryEnqueue(() =>
                    {
                        if (_closed) return;
                        HerbertStatusText.Text = "Herbert is active";
                        StartWebSocketRetry();
                    });
                }
            }
            catch (Exception ex)
            {
                Debug.WriteLine($"[MainWindow] Container start failed: 0x{ex.HResult:X8} {ex.Message}\n{ex.StackTrace}");
                // Write error to separate crash log file (main log may be locked by StreamWriter)
                try
                {
                    File.WriteAllText(@"C:\temp\Herbert\crash.log",
                        $"[{DateTime.Now:HH:mm:ss}] STARTUP EXCEPTION: {ex.GetType().Name}: {ex.Message}\n" +
                        $"  HResult: 0x{ex.HResult:X8}\n" +
                        $"  Stack: {ex.StackTrace}\n" +
                        (ex.InnerException != null ? $"  Inner: {ex.InnerException.GetType().Name}: {ex.InnerException.Message}\n" : ""));
                }
                catch { }
                _dispatcherQueue?.TryEnqueue(() =>
                {
                    if (!_closed) HerbertStatusText.Text = "Herbert failed to start";
                });
            }
        });
    }

    private void OnContainerOutput(string text)
    {
        if (_suppressContainerOutput) return;

        lock (_logLock)
        {
            _pendingOutput.Append(text);
        }

        _dispatcherQueue?.TryEnqueue(() =>
        {
            if (_closed) return;

            string pending;
            lock (_logLock)
            {
                pending = _pendingOutput.ToString();
                _pendingOutput.Clear();
            }

            if (string.IsNullOrEmpty(pending)) return;
            AppendToLog(pending);
        });
    }

    private void OnContainerStatus(string text)
    {
        _dispatcherQueue?.TryEnqueue(() =>
        {
            if (_closed) return;
            LogHeaderText.Text = $"Live Trading Output \u2014 {text}";
        });
    }

    // ========== WebSocket Trade Feed ==========

    private void StartWebSocketRetry()
    {
        if (_closed) return;

        Debug.WriteLine("[MainWindow] Starting WebSocket retry timer");
        AppendToLog("\n\u23F3 Waiting for Herbert's trade feed...\n");

        _wsRetryTimer = new DispatcherTimer { Interval = TimeSpan.FromSeconds(3) };
        _wsRetryTimer.Tick += (_, _) =>
        {
            if (_closed || _wsConnected) return;
            _ = AttemptWebSocketConnectAsync();
        };
        _wsRetryTimer.Start();

        _ = AttemptWebSocketConnectAsync();
    }

    private async Task AttemptWebSocketConnectAsync()
    {
        if (_closed || _wsConnected) return;

        _wsRetryCount++;
        Debug.WriteLine("[MainWindow] WebSocket connect attempt");

        try
        {
            var ws = new System.Net.WebSockets.ClientWebSocket();
            _wsCts = new CancellationTokenSource(TimeSpan.FromSeconds(5));

            await ws.ConnectAsync(new Uri("ws://localhost:8765"), _wsCts.Token);

            if (_closed) { ws.Dispose(); return; }

            _wsConnected = true;
            _webSocket = ws;
            _suppressContainerOutput = true;
            Debug.WriteLine("[MainWindow] WebSocket connected!");

            _dispatcherQueue?.TryEnqueue(() =>
            {
                if (_closed) return;
                _wsRetryTimer?.Stop();
                _logBuffer.Clear();
                AppendToLog("\U0001F4C8 Connected to Herbert's Trade Feed\n");
                AppendToLog("\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\n\n");
                LogHeaderText.Text = "Live Trading Output \u2014 Connected \u2705";
            });

            // Start reading messages
            _ = ReadWebSocketMessagesAsync(ws);
        }
        catch
        {
            Debug.WriteLine("[MainWindow] WebSocket connect failed, will retry");
        }
    }

    private async Task ReadWebSocketMessagesAsync(System.Net.WebSockets.ClientWebSocket ws)
    {
        var buffer = new byte[8192];
        try
        {
            while (!_closed && ws.State == System.Net.WebSockets.WebSocketState.Open)
            {
                var result = await ws.ReceiveAsync(buffer, CancellationToken.None);
                if (result.MessageType == System.Net.WebSockets.WebSocketMessageType.Close)
                    break;

                var json = Encoding.UTF8.GetString(buffer, 0, result.Count);
                OnWebSocketMessage(json);
            }
        }
        catch { /* ignore */ }

        // Connection lost — restart retry
        _wsConnected = false;
        Debug.WriteLine("[MainWindow] WebSocket closed, will retry");
        _dispatcherQueue?.TryEnqueue(() =>
        {
            if (!_closed) _wsRetryTimer?.Start();
        });
    }

    private void OnWebSocketMessage(string json)
    {
        if (_closed) return;

        _dispatcherQueue?.TryEnqueue(() =>
        {
            try
            {
                if (_closed) return;

                using var doc = JsonDocument.Parse(json);
                var root = doc.RootElement;

                if (!root.TryGetProperty("type", out var typeProp) || typeProp.GetString() != "trade")
                    return;

                var formatted = FormatTradeMessage(root);
                AppendToLog(formatted + "\n");
            }
            catch { /* ignore */ }
        });
    }

    private static string FormatTradeMessage(JsonElement obj)
    {
        var timestamp = obj.GetProperty("timestamp").GetString() ?? "";
        var action = obj.GetProperty("action").GetString() ?? "";
        var symbol = obj.GetProperty("symbol").GetString() ?? "";
        var quantity = obj.GetProperty("quantity").GetInt32();
        var price = obj.GetProperty("price").GetDouble();
        var total = obj.GetProperty("total").GetDouble();
        var pnl = obj.GetProperty("pnl").GetDouble();

        var sb = new StringBuilder();
        sb.Append($"[{timestamp}]  ");

        sb.Append(action == "BUY" ? "\U0001F7E2 BUY  " : "\U0001F534 SELL ");

        sb.Append($"{symbol,-6}  ");
        sb.Append($"x{quantity,-4}  ");
        sb.Append($"@ ${price:F2}  ");
        sb.Append($"(${total:F2})  ");

        sb.Append(pnl >= 0 ? $"PnL: +${pnl:F2}" : $"PnL: -${-pnl:F2}");

        return sb.ToString();
    }

    // ========== UI Helpers ==========

    private void AppendToLog(string text)
    {
        _logBuffer.Append(text);

        if (_logBuffer.Length > MaxLogChars)
        {
            var trimmed = _logBuffer.ToString(
                _logBuffer.Length - (MaxLogChars - 10_000),
                MaxLogChars - 10_000);
            _logBuffer.Clear();
            _logBuffer.Append(trimmed);
        }

        LogTextBlock.Text = _logBuffer.ToString();
        ScrollToBottom();
    }

    private void ScrollToBottom()
    {
        LogScrollViewer.UpdateLayout();
        LogScrollViewer.ChangeView(null, LogScrollViewer.ScrollableHeight, null);
    }

    // ========== File Browser ==========

    private void RefreshFileTree()
    {
        if (_closed) return;

        FileTreeView.RootNodes.Clear();
        _nodePathMap.Clear();

        try
        {
            if (Directory.Exists(HerbertFolder))
            {
                PopulateDirectoryNode(HerbertFolder, FileTreeView.RootNodes);
            }
        }
        catch { /* ignore */ }
    }

    private void PopulateDirectoryNode(string dirPath, IList<TreeViewNode> nodes)
    {
        try
        {
            // Directories first
            foreach (var dir in Directory.GetDirectories(dirPath))
            {
                var name = Path.GetFileName(dir);
                var dirNode = new TreeViewNode
                {
                    Content = $"\U0001F4C1 {name}",
                    IsExpanded = false
                };

                PopulateDirectoryNode(dir, dirNode.Children);
                nodes.Add(dirNode);
            }

            // Files (skip hidden debug files)
            foreach (var file in Directory.GetFiles(dirPath))
            {
                var name = Path.GetFileName(file);
                if (HiddenFiles.Contains(name)) continue;

                var displayText = $"\U0001F4C4 {name}";
                var fileNode = new TreeViewNode { Content = displayText };

                var relPath = Path.GetRelativePath(HerbertFolder, file);
                _nodePathMap[relPath] = file;

                var parentName = Path.GetFileName(dirPath);
                _nodePathMap[$"{displayText}|{parentName}"] = file;

                nodes.Add(fileNode);
            }
        }
        catch { /* ignore */ }
    }

    private void OnFileInvoked(TreeView sender, TreeViewItemInvokedEventArgs args)
    {
        if (_closed) return;

        try
        {
            var displayText = args.InvokedItem?.ToString();
            if (string.IsNullOrEmpty(displayText)) return;

            // Only handle file nodes (not directories)
            if (!displayText.StartsWith("\U0001F4C4 ")) return;

            var fileName = displayText[3..]; // skip "📄 "

            // Find the full path
            string? fullPath = null;

            bool FindInNodes(IList<TreeViewNode> nodeList, string parentDirName)
            {
                foreach (var node in nodeList)
                {
                    var nodeText = node.Content?.ToString() ?? "";

                    if (nodeText == displayText)
                    {
                        var key = $"{displayText}|{parentDirName}";
                        if (_nodePathMap.TryGetValue(key, out var path))
                        {
                            fullPath = path;
                            return true;
                        }
                    }

                    if (node.Children.Count > 0)
                    {
                        var dirName = nodeText.StartsWith("\U0001F4C1 ") ? nodeText[3..] : nodeText;
                        if (FindInNodes(node.Children, dirName))
                            return true;
                    }
                }
                return false;
            }

            FindInNodes(FileTreeView.RootNodes, "Documents");

            if (fullPath == null)
            {
                // Fallback: search by filename
                foreach (var kvp in _nodePathMap)
                {
                    if (kvp.Value.EndsWith(fileName, StringComparison.OrdinalIgnoreCase))
                    {
                        fullPath = kvp.Value;
                        break;
                    }
                }
            }

            if (fullPath != null)
                ShowFileContent(fullPath, fileName);
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[MainWindow] OnFileInvoked exception: {ex.Message}");
        }
    }

    private async void ShowFileContent(string filePath, string fileName)
    {
        try
        {
            var content = await File.ReadAllTextAsync(filePath);

            // Truncate for display
            if (content.Length > 10_000)
                content = content[..10_000] + "\n\n... (truncated)";

            var dialog = new ContentDialog
            {
                Title = fileName,
                Content = new ScrollViewer
                {
                    Content = new TextBlock
                    {
                        Text = content,
                        FontFamily = new Microsoft.UI.Xaml.Media.FontFamily("Cascadia Code, Consolas, Courier New"),
                        FontSize = 12,
                        TextWrapping = Microsoft.UI.Xaml.TextWrapping.Wrap,
                        IsTextSelectionEnabled = true
                    },
                    MaxHeight = 500
                },
                CloseButtonText = "Close",
                XamlRoot = Content.XamlRoot
            };

            await dialog.ShowAsync();
        }
        catch (Exception ex)
        {
            Debug.WriteLine($"[MainWindow] ShowFileContent error: {ex.Message}");
        }
    }
}
