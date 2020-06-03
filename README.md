## 防火墙配置脚本

配置防火墙

```bash
sudo apt install iptables-persistent
iptables-restore < ./ruleset
netfilter-persistent save
```

修改 `subscribe.py` 中用户名和密码配置，将 {'USER': 'PASSWORD'} 替换为自定义的用户名和密码

```bash
virtualenv venv
source ./venv/bin/activate
chmod +x update_ip.sh
python subscribe.py
```
