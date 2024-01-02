# C305 Http Server

## Requirement

```sh
pip install -r requirements.txt
```

## Useage

```shell
python server.py -i ${bind ip} -p ${bind port} -e true/false #enable/disable encryption
python client.py -i ${addr} -p {port} # this client only use for encrypted connection
```

## Basic

没什么说的

## Bonus

### Encryption

先运行运行根目录下 `./encrypted_server.sh`, 然后运行 `./encrypted_client.sh`

client 指令说明:

- get: 输入要访问的文件夹路径
- post:
  - upload: 分别输入本地文件路径和上传到服务器的路径
  - delete：输入要删除文件的服务器路径

### Breakpoint Transmission

开个浏览器下载然后暂停

## 碎碎念

整个 project 需求设计突出一个乱。文档解释和需求混杂，找要求满篇文档乱找。测试脚本依托，用的 jupyter 然后正确答案还不单独写出来，运行一遍输出就给覆盖了。最终答辩的测试和测速居然是在实验室一台 i7-7700k 的电脑上上用 socket 自己发自己收？最终测试脚本突出一个黑盒，光看着冒出 testx 然后什么具体信息没有。然后目标电脑上甚至环境没配好，库没装全。测试的 demo 放 bb 上，通知方式不是邮件不是发群公告而是一个 @全体成员 😅

评价是整门课依托，管理混乱。理论课干念 ppt, 实验课华为 ensp 远古 virtubox 配环境致命打击（不关内存完整性保护装不上），然后 lab2 assignment 配路由突出一个混乱和意义不明。

为什么在这碎碎念？因为教工部出了评教送积分的司马政策，评教率疑似有点高了，有待降低。

