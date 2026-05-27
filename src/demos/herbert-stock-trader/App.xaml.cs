using System.Diagnostics;
using Microsoft.UI.Xaml;

namespace HerbertStockTrader;

public partial class App : Application
{
    private Window? _window;

    public App()
    {
        InitializeComponent();

        UnhandledException += (_, e) =>
        {
            Debug.WriteLine($"[App] UNHANDLED EXCEPTION: 0x{e.Exception.HResult:X8} {e.Message}");
            e.Handled = true;
        };
    }

    protected override void OnLaunched(LaunchActivatedEventArgs args)
    {
        _window = new MainWindow();
        _window.Activate();
    }
}
