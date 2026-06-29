---
title: GCC 编译过程
date: 2025-07-17 15:56:00 +0800
categories: [Linux 打包]
tags: [gcc]
---

## 概述

GCC 编译 C/C++ 代码的过程主要分为如下图的 4 个步骤（_`.i` 和 `.ii` 分别是 `.c` 和 `.cpp` 源文件预处理后的中间文件后缀名；`.o` 和 `.obj` 分别是 `Linux` 和 `Windows` 系统上汇编后的目标文件后缀名；`.a` 和 `.lib` 分别是 `Linux` 和 `Windows` 系统上静态库文件后缀名；`.exe` 是 `Windows` 上可执行文件后缀名，`Linux` 上可执行文件无后缀名；另外，`.so` 和 `.dll` 分别是 `Linux` 和 `Windows` 系统上动态库文件后缀名；**本文只是借用该图所表示的流程，不讨论 Windows 相关内容**_）：

![gcc_compilation_process](/assets/img/linux-packaging/gcc_compilation_process.png)

后续章节我们将以 `main.c`, `utils.h`, `utils.c` 这几个文件（都在同一目录下）为例，分别对这几个步骤进行详细说明，这几个文件的源码分别如下：

```c
// main.c
#include <stdio.h>
#include "utils.h"

int main() {
    printf("1 + 1 = %d\n", add(1, 1));
    return 0;
}
```

```c
// utils.h
int add(int a, int b);
int sub(int a, int b);
int mul(int a, int b);
int div(int a, int b);
```

```c
// utils.c
#include "utils.h"

int add(int a, int b)
{
    return a + b;
}

int sub(int a, int b)
{
    return a - b;
}

int mul(int a, int b)
{
    return a * b;
}

int div(int a, int b)
{
    return a / b;
}
```

## 预处理（Preprocessing）

预处理主要做了以下这些方面的工作：
- 插入头文件（`#include`）。
- 展开宏定义（`#define`）。
- 处理条件编译（`#if`, `#elif`, `#else`, `#endif`, `#ifdef`）。
- 保留 `#pragma` 指令，编译器需要使用。
- 删除注释。
- 添加行号和文件名标识，比如 `# 4 "main.c" 2`，便于编译报错和调试。

可以使用如下命令对 `main.c` 做预处理：
```console
$ gcc -E -I. -o main.i main.c
```

- `-E`: 表示只做预处理。
- `-I.`: 表示把当前工作目录 `.` 添加到头文件搜索目录列表中。
- `-o main.i`: 表示把结果输出到 `main.i` 文件中。

预处理生成的中间文件 `main.i` 有很多内容，这里只展示一下最后包含 `main.c` 源码的部分：
```c
# 943 "/usr/include/stdio.h" 3 4

# 3 "main.c" 2
# 1 "./utils.h" 1

int add(int a, int b);
int sub(int a, int b);
int mul(int a, int b);
int div(int a, int b);
# 4 "main.c" 2

int main() {
    printf("1 + 1 = %d\n", add(1, 1));
    return 0;
}
```

C/C++ 语言中包含头文件的写法有如下 2 种：
- **尖括号形式**: `#include <stdio.h>`，通常用于包含系统头文件。
- **双引号形式**: `#include "mylib.h"`，通常用于包含用户头文件。

可以添加头文件搜索目录列表的 GCC 参数如下（更多细节说明请参考[官方手册](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Directory-Options.html#index-I)）：
- `-I dir`: 把 _dir_ 添加到头文件搜索目录列表（用户级）。
- `-iquote dir`: 把 _dir_ 添加到头文件搜索目录列表（用户级），仅适用于`双引号形式`。
- `-isystem dir`: 把 _dir_ 添加到头文件搜索目录列表（系统级）。
- `-idirafter dir`: 把 _dir_ 添加到头文件搜索目录列表（系统级），优先级低于 `isystem`。

以上这些参数都可以在命令行里指定多次，GCC 会根据指定的顺序依次都添加到搜索目录列表中。

GCC 对于系统头文件和用户头文件会有不同的处理，比如系统头文件会抑制所有告警（即不打印编译告警信息），关于系统头文件的说明，请参考[官方手册](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/cpp/System-Headers.html)。

可以添加头文件搜索目录列表的环境变量如下（更多细节说明请参考[官方手册](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Environment-Variables.html#index-CPATH)）：
- `CPATH`: 对所有语言有效（除 C/C++ 外，GCC 还可以编译 Go, Objective-C/C++, Fortran, Rust 等），效果等同于 `-I` 参数，但是优先级低于 `-I`。
- `C_INCLUDE_PATH`: 仅对 C 语言有效，效果等同于 `-isystem` 参数，但优先级低于 `-isystem`，也低于 `CPATH`。
- `CPLUS_INCLUDE_PATH`: 仅对 C++ 语言有效，效果等同于 `-isystem` 参数，但优先级低于 `-isystem`，也低于 `CPATH`。

以上这些环境变量中可以同时添加多个目录，用 `PATH_SEPARATOR` 进行分隔，Linux 通常为冒号（`:`），Windows 为分号（`;`）。也可以包含空路径（整个为空，或者开头/结尾为空，如 `:/my/include`），当包含空路径时，相当于添加了当前工作目录（`.`）。

GCC 在被编译时，会根据编译参数和自身内部逻辑判断，生成一个`默认系统头文件搜索目录列表`，具体生成逻辑较为复杂，但是我们可以通过如下命令查看具体有哪些目录（前提是没有命令行参数和环境变量指定，如果有，该命令也会同时打印出来，就不仅仅是默认系统头文件搜索目录列表了）：

```console
$ gcc -E -xc -v - < /dev/null 
...
#include "..." search starts here:
#include <...> search starts here:
 /usr/lib/gcc/x86_64-redhat-linux/4.8.5/include
 /usr/local/include
 /usr/include
End of search list.
...
```

GCC 在编译 C/C++ 时头文件搜索目录优先级如下：
1. 如果是`双引号形式`，搜索被编译源文件所在目录。
2. 如果是`双引号形式`，搜索 `-iquote` 参数指定的目录。
3. 搜索 `-I` 参数指定的目录。
4. 搜索 `CPATH` 环境变量指定的目录。
5. 搜索 `-isystem` 参数指定的目录。
6. 搜索 `C_INCLUDE_PATH`/`CPLUS_INCLUDE_PATH` 环境变量指定的目录。
7. 搜索默认系统头文件目录。
8. 搜索 `-idirafter` 参数指定的目录。

## 编译（Compilation）

编译是把预处理后的中间文件编译为汇编源文件（`.s`），可使用如下命令进行编译：
```console
$ gcc -S -o main.s main.i
```

- `-S`: 表示只做编译，不进行汇编和链接。
- `-o main.s`: 表示把结果输出到 `main.s` 文件中。

编译后生成的汇编源文件内容如下：
```console
$ cat main.s
        .file   "main.c"
        .section        .rodata
.LC0:
        .string "1 + 1 = %d\n"
        .text
        .globl  main
        .type   main, @function
main:
.LFB0:
        .cfi_startproc
        pushq   %rbp
        .cfi_def_cfa_offset 16
        .cfi_offset 6, -16
        movq    %rsp, %rbp
        .cfi_def_cfa_register 6
        movl    $1, %esi
        movl    $1, %edi
        call    add
        movl    %eax, %esi
        movl    $.LC0, %edi
        movl    $0, %eax
        call    printf
        movl    $0, %eax
        popq    %rbp
        .cfi_def_cfa 7, 8
        ret
        .cfi_endproc
.LFE0:
        .size   main, .-main
        .ident  "GCC: (GNU) 4.8.5 20150623 (Red Hat 4.8.5-44)"
        .section        .note.GNU-stack,"",@progbits
```

## 汇编（Assemble）

编译是把预处理后的中间文件编译为汇编源文件（`.s`），可使用如下命令进行汇编：
```console
$ gcc -c -o main.o main.s
```

- `-c`: 表示只做编译和汇编，不进行链接。
- `-o main.o`: 表示把结果输出到 `main.o` 文件中。

汇编后生成目标机器指令的目标文件 `main.o`，可以用 `readelf -s main.o` 查看其符号表：
```console
$ readelf -s main.o 

Symbol table '.symtab' contains 12 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     0: 0000000000000000     0 NOTYPE  LOCAL  DEFAULT  UND 
     1: 0000000000000000     0 FILE    LOCAL  DEFAULT  ABS main.c
     2: 0000000000000000     0 SECTION LOCAL  DEFAULT    1 
     3: 0000000000000000     0 SECTION LOCAL  DEFAULT    3 
     4: 0000000000000000     0 SECTION LOCAL  DEFAULT    4 
     5: 0000000000000000     0 SECTION LOCAL  DEFAULT    5 
     6: 0000000000000000     0 SECTION LOCAL  DEFAULT    7 
     7: 0000000000000000     0 SECTION LOCAL  DEFAULT    8 
     8: 0000000000000000     0 SECTION LOCAL  DEFAULT    6 
     9: 0000000000000000    43 FUNC    GLOBAL DEFAULT    1 main
    10: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND add
    11: 0000000000000000     0 NOTYPE  GLOBAL DEFAULT  UND printf
```

## 链接（Linking）

链接过程主要是把目标文件们的`代码段`和`数据段`拆分后，再加上引用的库和文件头部信息，最后组装成一个可执行文件。

可使用如下命令进行链接（由于输入的是 `main.o` 文件，所以 GCC 只需执行链接操作）：
```console
$ gcc -o main main.o -L. -lutils
```

- `-o main`: 表示把结果输出到 `main` 文件中。
- `-L.`: 表示把当前工作目录 `.` 添加到库文件搜索目录列表中。
- `-lutils`: 表示需要链接 `libutils.a` 或 `libutils.so` 库文件。

可以使用 `readelf -h main` 查看可执行文件的头部信息：
```console
$ readelf -h main
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 00 00 00 00 00 00 00 00 00 
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - System V
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x400470
  Start of program headers:          64 (bytes into file)
  Start of section headers:          6584 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         9
  Size of section headers:           64 (bytes)
  Number of section headers:         30
  Section header string table index: 29
``` 

GCC 链接库文件时优先查找动态库文件（`.so`），如果动态库文件不存在则查找静态库文件（`.a`），但是也可以通过参数 `-static` 强制只链接静态库文件，或者可以通过参数 `-Wl,-Bstatic` 或 `-Wl,-Bdynamic` 指定某些库只链接静态库或只链接动态库（详情请参考[链接器参数说明](https://sourceware.org/binutils/docs/ld/Options.html)）。

GCC 链接静态库文件时会把静态库文件的内容插入到目标文件中，链接动态库文件时只是在目标文件中记录链接信息，目标文件运行时由动态库链接器（`ld.so`）根据链接信息去查找和加载对应的动态库，动态库的查找顺序请参考《[Linux 上 ELF 文件依赖库的查找顺序](/posts/the-searching-order-of-elf-file-deps/)》。

GCC 在搜索库文件时的优先级如下：
1. 搜索 `-L` [参数](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Directory-Options.html#index-L)指定的目录。
2. 搜索 `LIBRARY_PATH` [环境变量](https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Environment-Variables.html#index-LIBRARY_005fPATH)指定的目录。
3. 搜索默认库文件目录。

GCC 在被编译时，会根据编译参数和自身内部逻辑判断，生成一个`默认库文件搜索目录列表`，具体生成逻辑较为复杂，但是我们可以通过如下命令查看具体有哪些目录（前提是没有命令行参数和环境变量指定，如果有，该命令也会同时打印出来，就不仅仅是默认库文件搜索目录列表了）：

```console
$ gcc -print-search-dirs -o main main.c -L. -lutils | grep libraries | sed 's/libraries: *=//' | tr ':' '\n'
/usr/lib/gcc/x86_64-redhat-linux/4.8.5/
/usr/lib/gcc/x86_64-redhat-linux/4.8.5/../../../../x86_64-redhat-linux/lib/x86_64-redhat-linux/4.8.5/
/usr/lib/gcc/x86_64-redhat-linux/4.8.5/../../../../x86_64-redhat-linux/lib/../lib64/
/usr/lib/gcc/x86_64-redhat-linux/4.8.5/../../../x86_64-redhat-linux/4.8.5/
/usr/lib/gcc/x86_64-redhat-linux/4.8.5/../../../../lib64/
/lib/x86_64-redhat-linux/4.8.5/
/lib/../lib64/
/usr/lib/x86_64-redhat-linux/4.8.5/
/usr/lib/../lib64/
/usr/lib/gcc/x86_64-redhat-linux/4.8.5/../../../../x86_64-redhat-linux/lib/
/usr/lib/gcc/x86_64-redhat-linux/4.8.5/../../../
/lib/
/usr/lib/
```

## 参考资料

- [GCC and Make] : https://www3.ntu.edu.sg/home/ehchua/programming/cpp/gcc_make.html
- [Options for Directory Search] : https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Directory-Options.html
- [Environment Variables Affecting GCC] : https://gcc.gnu.org/onlinedocs/gcc-15.1.0/gcc/Environment-Variables.html
- [Installing GCC: Configuration] : https://gcc.gnu.org/install/configure.html
- [ld Command-line Options] : https://sourceware.org/binutils/docs/ld/Options.html
- 《嵌入式C语言自我修养：从芯片、编译器到操作系统》
- 《程序员的自我修养：链接、装载与库》
