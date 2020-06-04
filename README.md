## 防火墙配置脚本

#### 环境配置

配置防火墙

```bash
sudo apt install iptables-persistent
iptables-restore < ./ruleset
netfilter-persistent save
```

修改 `subscribe.py` 中用户名和密码配置，将 {'USER': 'PASSWORD'} 替换为自定义的用户名和密码，

```bash
openssl rand -hex 12
```

更改 `tools.auth_digest.key` 值为上面生成的随机key

#### 启动网页

运行 subscribe.py 后，会将认证网页自动放到后台进程

```bash
virtualenv venv
source ./venv/bin/activate
pip install cherrypy
chmod +x update_ip.sh
python subscribe.py
```

此时，可以访问 `http://host_ip:8080` 来访问认证页面，成功输入用户名密码后，可以指定ip或自动检测客户端ip，添加到防火墙白名单中

#### 通过 curl 命令远程添加 ip 到白名单

通过 POST 请求可以远程添加ip，当login后确省ip参数时，会自动添加客户端ip

```bash
curl -X POST --anyauth -u user:password \
     --header "Content-Type:application/json" \
     -d '{"user-name":"user", "password": "password"}' http://host_ip:8080/login\?ip\=your_ip
```

手动获取当前 ip

```bash
ssh -tt user@host "who am i --ips | awk '{print \$6}'"
```

#### 停止网页

使用 pgrep 命令查找后台进程的 pid

```bash
pgrep python
kill 3912
```