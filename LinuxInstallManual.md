# 易度项目管理系统安装手册 #

## 此手册对应于ubuntu ##

### 系统要求 ###

1. 安装python2.4,和一些必要的编译库文件支持，在ubuntu下直接使用apt-get命令安装
```
sudo apt-get install build-essential
sudo apt-get install python2.4
sudo apt-get install python2.4-dev
sudo apt-get libxml2-dev
```

2. 下载解压[everydo-project](http://everydo-project.googlecode.com/files/everydo-project-1.1.tar.gz)包

```
tar xzvf everydo-project-1.1.tar.gz
cd everydo-project
python2.4 bootstrap.py
```

3. 用编辑器打开buildout.cfg,找到以下的代码块,定义实例监听端口和ZMI用户名和密码

```
[instance]
recipe = plone.recipe.zope2instance
eggs = 
    ${buildout:eggs}
    ${plone:eggs}
zope2-location = ${zope2:location}
user = admin:123456
http-address = 8080
debug-mode = on
default-zpublisher-encoding = utf-8
deprecation-warnings = off
extra-paths = 
    ${zope2:location}/lib/python 
```

```
user = admin:123456
```
> 此处定义ZMI用户名和密码(例:用户名admin,密码123456)

```
http-address = 8080
```
> 此处定义ZOPE实例监听端口(例:监听8080端口)

4. build it !

执行命令
```
bin/buildout -v
```

**在buildout的过程中，会花费一点时间下载安装必要的组件，这取决于你当前网络的状况**

### 启动并安装易度项目管理应用 ###

1. 在启动之前，需要手动删除Zope2四行代码,否则会在启动时报以下错误:

```
   ConfigurationError: ('Invalid value for', 'handler', 'ImportError: Module zope.app.component.metaconfigure has no global defaultLayer')
```

2. 使用编辑器在当前目录下找到 parts/zope2/lib/python/Products/Five/meta.zcml  86行，删除以下字段

```
    <!-- BBB 2006/02/24, to be removed after 12 months -->
    <meta:directive
        name="defaultLayer"
        schema="zope.app.component.metadirectives.IDefaultLayerDirective"
        handler="zope.app.component.metaconfigure.defaultLayer"
        />`
```

3. 以调试模式启动应用

```
bin/instance fg
```

4. 使用浏览器访问 http://localhost:8080/manage , 使用用户名admin 和密码 admin 登入

![http://download.zopen.cn/installer/p1.png](http://download.zopen.cn/installer/p1.png)

5. 创建名为project的站点
  1. Id处填写: project
  1. Title处不修改
  1. Extension Profiles下拉找到basecamp site, 点击 Add Plone Site 完成安装的操作

**在创建站点的过程中，初始化数据会花费一点时间，请耐心等待完成。**

> ![http://download.zopen.cn/installer/p3.png](http://download.zopen.cn/installer/p3.png)

### 访问创建好的站点 ###

**创建成功后，会出现 Project (Site), 点击进入， 在上侧的控制栏，点击view浏览进入该站点**

![http://download.zopen.cn/installer/p4.png](http://download.zopen.cn/installer/p4.png)

![http://download.zopen.cn/installer/p5.png](http://download.zopen.cn/installer/p5.png)

**您也可以直接输入地址 http://localhost:8080/project 来进行访问，以之前创建站点名为project为例**

![http://download.zopen.cn/installer/p6.png](http://download.zopen.cn/installer/p6.png)

**以daemon模式启动实例**

> 执行命令

```
bin/instance start
```

### 设置虚拟主机 ###

**需要配置虚拟主机服务，否则在进入项目管理站点，点击一些页面时会出错**

1. 进入ZMI(http://localhost:8080/manage)

  * 找到virtual\_hosting，点击进入
![http://download.zopen.cn/installer/vir01.png](http://download.zopen.cn/installer/vir01.png)

  * 在右上角进入mapping
![http://download.zopen.cn/installer/vir02.png](http://download.zopen.cn/installer/vir02.png)

  * 在栏处编辑需要设置的虚拟主机，以project的站点为例

![http://download.zopen.cn/installer/vir03.png](http://download.zopen.cn/installer/vir03.png)


### 设置邮件发送服务器 ###

1. 进入ZMI(http://localhost:8080/manage)

2. 找到mailhost, 进入设置发送服务器信息

> 即可！