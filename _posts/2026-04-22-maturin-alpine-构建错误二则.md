---
layout: post
title:  "alpine 下 maturin 构建排错记录：两个典型问题"
date:   2026-04-22 18:05:58 +0800
categories: 计算机技术 错误
---

最近在 alpine 环境中使用 maturin 构建扩展时，遇到了两个典型问题。排查过程比较曲折，这里整理成一份可直接复用的排错记录。

## 摘要

1. 遇到 `libclang Dynamic loading not supported` 时，若构建命令显式传入 `--target`，可能导致已有的 musl 相关配置无法按预期生效。
2. 遇到 `libintl_dgettext: symbol not found` 时，需要在链接阶段补上 `intl` 库，例如设置 `RUSTFLAGS="-C link-arg=-lintl"`。

构建的基础镜像：quay.io/pypa/musllinux_1_2_x86_64

## 问题一：`libclang Dynamic loading not supported`

### 现象

```
  --- stderr
  ninja: entering directory '/build/target/x86_64-unknown-linux-musl/release/build/skia-bindings-1c81886fb916f8d7/out/skia'

  thread 'main' (2626) panicked at /root/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/bindgen-0.72.1/lib.rs:616:27:
  Unable to find libclang: "the `libclang` shared library at /usr/lib/llvm22/lib/libclang.so.22.1.3 could not be opened: Dynamic loading not supported"
  note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
💥 maturin failed
  Caused by: Failed to build a native library through cargo
  Caused by: Cargo build finished with "exit status: 101": `env -u CARGO PYO3_BUILD_EXTENSION_MODULE="1" PYO3_ENVIRONMENT_SIGNATURE="cpython-3.12-64bit" PYO3_PYTHON="/opt/python/cp312-cp312/bin/python" PYTHON_SYS_EXECUTABLE="/opt/python/cp312-cp312/bin/python" "cargo" "rustc" "--profile" "release" "--features" "vulkan,window,freetype" "--target" "x86_64-unknown-linux-musl" "--message-format" "json-render-diagnostics" "--manifest-path" "/build/Cargo.toml" "--lib"`
```

核心报错是 `libclang Dynamic loading not supported`。

### 排查

网上常见的解决方案是设置 `RUSTFLAGS=-Ctarget-feature=-crt-static`。实际上，[setuptools-rust](https://github.com/PyO3/setuptools-rust/blob/910fc604842ed37ed93aadbb5aef588af668d107/setuptools_rust/build.py#L545) 已经针对 musl 添加了这项配置。

但实际运行时问题依旧。经过一番排查后发现，只要在编译命令中加上 `--target` ，设置的 RUSTFLAGS 不会生效，就会同样触发该错误。（构建了一个最小的 rust-bindgen 例子用来排查。）
去掉这个选项后即可正常构建。（进一步确认后发现，使用 `--target` 会触发交叉编译。）

### 处理

因此在 `PyO3/maturin-action` 中，不应显式指定 `target`。

## 问题二：`libintl_dgettext: symbol not found`

### 现象

```
/tmp # python -c "import skia_canvas_pyr"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/usr/local/lib/python3.12/site-packages/skia_canvas_pyr/__init__.py", line 1, in <module>
    from .classes.canvas import Canvas, CanvasGradient, CanvasPattern, CanvasTexture
  File "/usr/local/lib/python3.12/site-packages/skia_canvas_pyr/classes/canvas.py", line 12, in <module>
    from ..skia_canvas_pyr import (
ImportError: Error relocating /usr/local/lib/python3.12/site-packages/skia_canvas_pyr/skia_canvas_pyr.cpython-312-x86_64-linux-musl.so: libintl_dgettext: symbol not found
```

### 处理

解决方法是设置 `RUSTFLAGS="-C link-arg=-lintl"`。

这个错误也比较奇怪：代码里调用了相关函数，却没有正确链接对应的动态库。怀疑是一些依赖库没有考虑过 musl 环境。
