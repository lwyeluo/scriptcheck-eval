### 配置chrome-remote-debugging
- [x] 为保证各个操作的顺利执行，在进行安装配偶之前，最好翻墙。同时，必须保证 nodejs 和 npm 安装完成。
- 执行安装命令：
```
npm install chrome-remote-interface
```
- [x] 在执行上面这条命令的时候可能会出现下面的报错;
```
npm WARN enoent ENOENT: no such file or directory, open '/package.json'
npm WARN !invalid#1 No description
npm WARN !invalid#1 No repository field.
npm WARN !invalid#1 No README data
npm WARN !invalid#1 No license field.
```
- 这个错误提示是因为本目录下没有packag.json。
```
使用下面的命令，生成一个默认的package.json文件
npm init -f
```
- 之后执行上述的安装命令，在后面碰到的问题中发现，使用下述命令进行全局安装较好。
```
sudo npm install -g chrome-remote-interface
出现下面的的输出表示安装成功：
/usr/local/bin/chrome-remote-interface -> /usr/local/lib/node_modules/chrome-remote-interface/bin/client.js
/usr/local/lib
└─┬ chrome-remote-interface@0.27.1 
  ├── commander@2.11.0 
  └─┬ ws@6.2.1 
    └── async-limiter@1.0.0
```
- 此时输入**chrome-remote-interface**命令 来检查安装情况。

- 在进行debugging的时候一定要在一个终端中输入下面的命令来开启相应的端口进行调试：
```
google-chrome --remote-debugging-port=9222
```

-之后再另一个终端中进行相应代码的执行来记性调试。