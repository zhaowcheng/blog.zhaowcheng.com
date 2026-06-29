---
title: 使用 iptables 为 KVM 虚拟机实现桥接网络
date: 2025-02-21 20:59:00 +0800
categories: [计算机网络]
tags: [network, kvm, bridge, iptables]
---

## 适用场景

我把一台笔记本电脑安装了 Linux，准备用来作为 KVM 虚拟机服务器，这台笔记本只有无线网卡，当我想把这个无线网卡桥接到虚拟机时，始终无法成功，网上也查了很多资料，始终没有解决。

最终决定放弃桥接网络，改用 NAT 端口转发来实现外部访问虚拟机，然后参考了 Libvirt [文档](https://wiki.libvirt.org/Networking.html#forwarding-incoming-connections) 通过 iptables 配置了端口转发，用了一段时间后发现把这个配置稍加改造就可以达到和桥接网络一样的效果。

## 如何实现

笔记本网卡信息如下（`wlp0s20f3` 是无线网卡，`virbr0` 是安装 KVM 后自动生成的虚拟网卡）：

```console
$ ip address 
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: wlp0s20f3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 74:3a:f4:35:c1:cc brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.100/24 brd 192.168.1.255 scope global noprefixroute wlp0s20f3
       valid_lft forever preferred_lft forever
    inet6 240e:333:2bba:cb00:fb2:52e7:1762:b80f/64 scope global temporary dynamic 
       valid_lft 213162sec preferred_lft 86001sec
    inet6 240e:333:2bba:cb00:4931:9362:97c8:57e9/64 scope global dynamic mngtmpaddr noprefixroute 
       valid_lft 213162sec preferred_lft 126762sec
    inet6 fe80::daca:13ec:24af:c779/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
3: virbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default qlen 1000
    link/ether 52:54:00:ab:7d:a0 brd ff:ff:ff:ff:ff:ff
    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0
       valid_lft forever preferred_lft forever
```

我安装了 3 台虚拟机：

```console
$ virsh list --all
 Id   Name             State
---------------------------------
 -    el7-x86_64-101   shut off
 -    el7-x86_64-102   shut off
 -    el7-x86_64-103   shut off
```

为这 3 台虚拟机配置静态 IP 地址，信息如下：

| 虚拟机 | IP | 网关 | DNS |
| --- | --- | --- | --- |
| el7-x86_64-101 | 192.168.122.101/24 | 192.168.122.1 | 192.168.122.1 |
| el7-x86_64-102 | 192.168.122.102/24 | 192.168.122.1 | 192.168.122.1 |
| el7-x86_64-103 | 192.168.122.103/24 | 192.168.122.1 | 192.168.122.1 |

为了能从其他电脑直接访问这 3 台虚拟机，需要为这 3 台虚拟机分别分配一个外部可以访问的 IP（即与无线网卡 `wlp0s20f3` 在同一网段内的 IP 地址），分配如下：

| 虚拟机 | 外部 IP |
| --- | --- |
| el7-x86_64-101 | 192.168.1.101/24 |
| el7-x86_64-102 | 192.168.1.102/24 |
| el7-x86_64-103 | 192.168.1.103/24 |

接下来就把分配的这 3 个 外部 IP 都配置到无线网卡 `wlp0s20f3` 上，配置后信息如下：

```console
$  ip address 
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host noprefixroute 
       valid_lft forever preferred_lft forever
2: wlp0s20f3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 74:3a:f4:35:c1:cc brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.100/24 brd 192.168.1.255 scope global noprefixroute wlp0s20f3
       valid_lft forever preferred_lft forever
    inet 192.168.1.101/24 brd 192.168.1.255 scope global secondary noprefixroute wlp0s20f3
       valid_lft forever preferred_lft forever
    inet 192.168.1.102/24 brd 192.168.1.255 scope global secondary noprefixroute wlp0s20f3
       valid_lft forever preferred_lft forever
    inet 192.168.1.103/24 brd 192.168.1.255 scope global secondary noprefixroute wlp0s20f3
       valid_lft forever preferred_lft forever
    inet6 240e:333:2bba:cb00:fb2:52e7:1762:b80f/64 scope global temporary dynamic 
       valid_lft 213162sec preferred_lft 86001sec
    inet6 240e:333:2bba:cb00:4931:9362:97c8:57e9/64 scope global dynamic mngtmpaddr noprefixroute 
       valid_lft 213162sec preferred_lft 126762sec
    inet6 fe80::daca:13ec:24af:c779/64 scope link noprefixroute 
       valid_lft forever preferred_lft forever
3: virbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default qlen 1000
    link/ether 52:54:00:ab:7d:a0 brd ff:ff:ff:ff:ff:ff
    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0
       valid_lft forever preferred_lft forever
```

配置完成后，只需执行如下几条命令就可以实现桥接网络的效果（相当于外部对 `192.168.1.101` 的访问都会被转发到 `192.168.122.101`，其他的依此类推）：

```console
$ iptables -t nat -I PREROUTING -d 192.168.1.101 -j DNAT --to-destination 192.168.122.101
$ iptables -t nat -I POSTROUTING -s 192.168.122.101 -j SNAT --to-source 192.168.1.101
$ iptables -I FORWARD -d 192.168.122.101 -m state --state NEW -j ACCEPT

$ iptables -t nat -I PREROUTING -d 192.168.1.102 -j DNAT --to-destination 192.168.122.102
$ iptables -t nat -I POSTROUTING -s 192.168.122.102 -j SNAT --to-source 192.168.1.102
$ iptables -I FORWARD -d 192.168.122.102 -m state --state NEW -j ACCEPT

$ iptables -t nat -I PREROUTING -d 192.168.1.103 -j DNAT --to-destination 192.168.122.103
$ iptables -t nat -I POSTROUTING -s 192.168.122.103 -j SNAT --to-source 192.168.1.103
$ iptables -I FORWARD -d 192.168.122.103 -m state --state NEW -j ACCEPT
```

通过 iptables 命令配置的规则在系统重启后会失效，为了能够持久生效，可以创建 [Libvirt Hook](https://libvirt.org/hooks.html#etc-libvirt-hooks-network) 脚本 `/etc/libvirt/hooks/network`，这样每次 Libvirt 服务启动时都会自动执行这个脚本，脚本内容如下：

```shell
#!/bin/bash
# Bridge by iptables.

set -e
set -u

bridge() {
    internal_ip="$1"
    external_ip="$2"

    iptables -t nat -I PREROUTING -d ${external_ip} -j DNAT --to-destination ${internal_ip}
    iptables -t nat -I POSTROUTING -s ${internal_ip} -j SNAT --to-source ${external_ip}
    iptables -I FORWARD -d ${internal_ip} -m state --state NEW -j ACCEPT

    echo "Bridged ${internal_ip} to ${external_ip}"
}

ifname="$1"
action="$2"
position="$3"

if [ $action == started ]; then
    bridge "192.168.122.101" "192.168.1.101"
    bridge "192.168.122.102" "192.168.1.102"
    bridge "192.168.122.103" "192.168.1.103"
fi
```

## 参考资料

- [Forwarding Incoming Connections] : https://wiki.libvirt.org/Networking.html#forwarding-incoming-connections
- [Hooks for specific system management] : https://libvirt.org/hooks.html#etc-libvirt-hooks-network
