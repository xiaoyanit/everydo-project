# 易度项目管理系统安装手册 #

<font color='red'>此程序只支持python2.4，请在安装前卸载当前系统的其他python版本</font> 

## 此手册对应于windows环境安装 ##

### 安装配置 ###

1. [下载安装程序](http://code.google.com/p/everydo-project/downloads/list), 执行该安装程序

2. 选择安装路径
> ![http://download.zopen.cn/installer/p0.0.png](http://download.zopen.cn/installer/p0.0.png)

3. 配置端口和管理员账户. 下面已设置访问端口为8080，管理员用户名和密码都为admin
> ![http://download.zopen.cn/installer/p0.png](http://download.zopen.cn/installer/p0.png)

4. 点击下一步进行安装

### 创建一个名为project的易度项目管理站点 ###

1. 在开始菜单中找到安装好的易度项目管理系统开源版本， 进入控制面板
> ![http://download.zopen.cn/installer/p0.1.png](http://download.zopen.cn/installer/p0.1.png)
> ![http://download.zopen.cn/installer/p0.2.png](http://download.zopen.cn/installer/p0.2.png)

2. 点击ZopeManageInterface进入ZMI,您也可以直接使用浏览器访问 http://localhost:8080/manage ,使用用户名admin和密码admin登入
> ![http://download.zopen.cn/installer/p1.png](http://download.zopen.cn/installer/p1.png)

3. 在页面的右侧的下拉栏处找到 Plone Site 点击Add进入
> ![http://download.zopen.cn/installer/p2.png](http://download.zopen.cn/installer/p2.png)

4. 创建名为project的站点
  1. Id处填写: project
  1. Title处不修改
  1. Extension Profiles下拉找到basecamp site, 点击 Add Plone Site 完成安装的操作

**在创建站点的过程中，初始化数据会花费一点时间，请耐心等待完成。**

> ![http://download.zopen.cn/installer/p3.png](http://download.zopen.cn/installer/p3.png)

### 访问创建好的站点 ###

**创建成功后，会出现 Project (Site), 点击进入， 在上侧的控制栏，点击view浏览进入该站点
> ![http://download.zopen.cn/installer/p4.png](http://download.zopen.cn/installer/p4.png)
> ![http://download.zopen.cn/installer/p5.png](http://download.zopen.cn/installer/p5.png)**

**您也可以直接输入地址 http://localhost:8080/project 来进行访问，以之前创建站点名为project为例
> ![http://download.zopen.cn/installer/p6.png](http://download.zopen.cn/installer/p6.png)**

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

<font color='red'>配置邮件通知，如没有配置此步，那么在添加人员和发送消息时请不要勾选邮件通知的选项，否则会报错 </font>

邮件通知服务配置很简单，支持SMTP发送邮件

1. 进入ZMI(http://localhost:8080/manage)

http://download.zopen.cn/installer/m1.PNG

2. 找到mailhost, 进入设置发送服务器信息

http://download.zopen.cn/installer/m0.PNG

3. 设置发送邮件服务器的发送人属性

在下图红框处，填写第一步的发送人帐号

![http://download.zopen.cn/installer/m2.png](http://download.zopen.cn/installer/m2.png)

Save Changes 即可！