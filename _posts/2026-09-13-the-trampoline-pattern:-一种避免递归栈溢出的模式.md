---
layout: post
title:  "The Trampoline Pattern: 一种避免递归栈溢出的模式"
date:   2026-09-13 17:19:51 +0800
categories: 计算机技术 递归
---


递归版本代码

```js
function sumTR(n, acc = 0) {
  if (n === 0) return acc;
  return sumTR(n - 1, acc + n);
}

sumTR(100000)
```

Tramoline 版本代码

```js
function trampoline(fn) {
  let result = fn;
  while (typeof result === 'function') {
    result = result();
  }
  return result;
}

function sumTrampoline(n, acc = 0) {
  if (n === 0) return acc;
  return () => sumTrampoline(n - 1, acc + n);
}

trampoline(() => sumTrampoline(100000)); // no stack overflow, still tail-recursive in spirit
```

参考： [Your Recursion Is Lying to You](https://blog.gaborkoos.com/posts/2026-05-09-Your-Recursion-Is-Lying-to-You/)

