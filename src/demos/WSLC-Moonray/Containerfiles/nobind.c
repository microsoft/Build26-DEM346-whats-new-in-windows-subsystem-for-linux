#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdarg.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <errno.h>

typedef long (*syscall_fn_t)(long number, ...);

long syscall(long number, ...) {
    // Make mbind and move_pages no-ops in containers
    if (number == __NR_mbind || number == __NR_move_pages) {
        return 0;
    }

    // Forward all other syscalls to the real implementation
    static syscall_fn_t real_syscall = NULL;
    if (!real_syscall) {
        real_syscall = (syscall_fn_t)dlsym(RTLD_NEXT, "syscall");
    }

    va_list args;
    va_start(args, number);
    long a1 = va_arg(args, long);
    long a2 = va_arg(args, long);
    long a3 = va_arg(args, long);
    long a4 = va_arg(args, long);
    long a5 = va_arg(args, long);
    long a6 = va_arg(args, long);
    va_end(args);

    return real_syscall(number, a1, a2, a3, a4, a5, a6);
}
