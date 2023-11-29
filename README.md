# ICPC 2023 合肥站选手机器镜像制作脚本

Base image: ICPC 2023 南京站镜像（ISO），其基于 ICPC World Final 20231005 镜像。

## 参考信息

- diff 目录：南京站镜像与 WF 1005 image 的差异。
- <https://help.ubuntu.com/community/LiveCDCustomization>: Ubuntu 官方 Wiki 的 LiveCD 魔改指南。
- LUG 与 Vlab 的 strap 系列仓库：
    - <https://github.com/USTC-vlab/labstrap>: 从 PVE 的 base LXC tarball 修改镜像。
    - <https://github.com/ustclug/liimstrap>: `debootstrap` 配置用于图书馆查询机的 NFS rootfs。
    - <https://github.com/ustclug/101strap>: `debootstrap` 配置用于 Linux 101 的虚拟机 OVF 文件。

## 使用

```shell
docker build -t icpcstrap .
```

然后：

```shell
docker run --rm -it --name=icpcstrap --privileged \
    -v "$(pwd)":/srv:ro \
    -v /path/to/output:/target \
    -v /path/to/image.iso:/input.iso:ro \
    -e ROOT_PASSWORD=root_password \
    -e ICPCSSID=ICPC_Contestant_WiFi \
    -e ICPCPASS=wifi_password \
    --ulimit nofile=1024 \
    icpcstrap
```

相关的中间产物和最终输出会在 `/path/to/output` 中。

### 清理

```shell
sudo rm -rf edit/ EFI.img mbr.img ubuntu-22.04.1-icpc2023-hefei-output-amd64.iso ubuntu-22.04.1-icpc2023-hefei-output-amd64.iso.sha512sum
```

### 环境变量

- 如果需要调试，可以添加 `-e DEBUG=true`。
- `unsquashfs` 很慢，所以一个额外的选项 `-e COPY_FROM_ORIGINAL=true` 每次会从 /target/edit-original 递归复制到 /target/edit 中。
    - 使用 `cp --reflink` 对 XFS/Btrfs 用户优化。
- `ICPCSSID` 与 `ICPCPASS` 用于设置 Wi-Fi 的 SSID 与密码。
    - 会在 `/etc/netplan/02-icpc-wifi.yaml` 中添加 Wi-Fi 的配置。
- `ROOT_PASSWORD` 设置 root 密码。
    - 如果不设置，会使用一个 base64 后的 12 随机字节作为 root 密码。

## 更改

1. 添加了 Wi-Fi 的 netplan 配置（我们得到的镜像没有这个）。

> [!CAUTION]  
> 假设无线网卡为 `wlp1s0`。

> [!NOTE]  
> 虚拟机测试时，该项配置可能导致开机较慢。可以考虑设置成一个无效值（比如说密码改成 8 位以下）。

2. 添加了 `/etc/skel/Desktop/seats.txt`，以便志愿者填写座位号。DOMjudge 的桌面快捷方式也添加了。

> [!CAUTION]  
> 在填写座位号之后，热身赛之前，做以下设置：
>
> 1. 将 `/home/icpc2023/Desktop/seats.txt` 的内容设置为 hostname。
> 2. 删除 `/etc/skel/Desktop/seats.txt`。
> 3. 删除 icpc2023 用户，新建 icpc 用户（具体备注见下）。

3. 类似 Vlab earlyoom 的设置。

> [!CAUTION]  
> 脚本 (`/etc/earlyoom-notif.sh`) 假设用户名为 icpc。

4. Root 公钥替换。

5. 设置了心跳脚本（需要配合服务器运行 `monitor/` 下的程序）。

> [!NOTE]  
> URL 环境变量存储在 `/etc/systemd/system/heartbeat.service.d/override.conf` 中。

6. 环境变量：设置在 `~/.config/environment.d/90icpc.conf` 中，`~/.profile` 会去 `source` 这个文件。

> [!NOTE]  
> 放在这里的环境变量可以正确被 systemd user service 读取，同时也能被其他应用程序使用。

> [!CAUTION]  
> 目前设置了 `SUBMITBASEURL`, `SUBMITCONTEST`。
> 有关 `SUBMITBASEURL`，可参考 <https://www.domjudge.org/docs/manual/8.2/install-workstation.html#command-line-submit-client>。这个变量也会被用来设置桌面上的快捷方式。

> [!CAUTION]  
> 运行时更新此文件后，直接注销后再登录可能无法生效。`loginctl terminate-user $USER` 强制注销后再登录应该能够解决问题。

7. 保留了一些（会被 autoremove 的）Python 3 的包。

> [!NOTE]  
> <https://image.icpc.global/icpc2023/pypy3.modules.txt> 中包含了一些模块，但是这些模块会被 autoremove 掉。
> 即使不定制镜像，安装器也会自行做 autoremove，所以我不知道这个列表是怎么回事——可能上游这个列表就是有 bug 的（至少看起来他们没有很仔细的考虑过这个问题）。
> 肉眼看的话，应该除了 python3-dateutil 以外，其他对比赛的影响可以忽略不计，并且 Python 在 ICPC 中也不是主流的选项。

> [!CAUTION]  
> 此修改也需要 judgehost 更新 chroot 目录。

8. 添加了 `/opt/set-autologin` 与 `/opt/set-nologin` 脚本，用于比赛开始/结束时设置自动登录 `icpc` 账户/取消自动登录。

> [!CAUTION]  
> 脚本不会自动执行，请准备好批量 SSH 的设施。

9. 不允许 suspend（避免选手误操作）。

> [!NOTE]  
> 默认设置下，普通用户不能够 hibernate, hybrid-sleep, suspend-then-hibernate，但是可以 suspend，并且某些键盘上会设置 suspend 按键导致误操作。

## 笔记

### 选手机配置

> [!NOTE]  
> ISO 支持无人值守安装 (preseed)，如果要在虚拟机中测试，注意选择 SATA 控制器后在 grub 中选择安装到 disk。
> 对于 KVM (libvirt) 用户，不要选择 VirtIO（Block）控制器，否则盘是 `/dev/vdx`，preseed 脚本会找不到。使用 VirtIO SCSI 可以正常测试（但是 virt-manager 里面应该没有这个选项）。

> [!CAUTION]  
> 官方 image 的无人值守安装会新建一个叫 icpc2023 的用户，密码是 passw0rd，正式部署的时候记得删除这个用户，并且新建名为 **icpc** 的用户（部分脚本中假设了这个用户名）。该用户**不**应该加入 sudoers 以及 wheel/adm 用户组。

> [!NOTE]  
> 接上，如果不想删用户，单纯修改 sudoers 是不够的，polkit 可能会允许特定的用户执行特定的命令（比如说修改 hostname）。

> [!NOTE]  
> `unsquashfs` 在文件描述符限制过大（几乎无限制）的时候会报 `FATAL ERROR: Data queue size is too large` 的错误。
> 一部分 docker daemon 会是这样——比如说 Arch Linux 的 docker.service。

> [!CAUTION]  
> 由于需要 U 盘启动，镜像未处理 usb-storage.ko。配置完成后需要手动删除以防止选手使用 U 盘：
>
> ```shell
> find /lib/modules -name usb-storage.ko -delete
> ```
>
> 或者
>
> ```shell
> find /lib/modules -name usb-storage.ko -exec mv {} {}.disabled \;
> ```

> [!NOTE]  
> 新建用户的参考命令：
>
> ```shell
> # 随机密码（不建议，如果机器网断了可能无法帮选手登录回自己的用户）
> # PASSWORD="$(head -c 6 /dev/urandom | base64)"
> # 或者一个已知的强密码
> PASSWORD="apasswordthatonlyyouknowpleasereplaceme"
> useradd -m -G teams -s /bin/bash -p "$(openssl passwd -6 "$PASSWORD")" icpc
> ```

> [!NOTE]  
> NTP 镜像未配置，需要配网完成后下发 `/etc/systemd/timesyncd.conf`。`systemd-timesyncd` 默认处于开启状态。

### 服务器配置

> [!NOTE]  
> 比赛服务器分为 Web 平台（domserver）和评测服务器（judgehost）两部分。
>
> 它们的相关配置在 `/opt/domjudge/etc` 下。
>
> 迁移服务器（网络后），judgehost 需要修改 `/opt/domjudge/judgehost/etc/restapi.secret` 中的地址，然后 `systemctl restart domjudge-judgehost.target` 重启评测服务（时间比较长），之后就能够在 domserver 管理员页面看到这些 judgehost 活过来了。

## Future work

### Nix?

用 nix 做一份 ICPC 标准镜像？不过这也不可能在合肥站实现，只能取决于有没有人感兴趣了。

### Rootfs's "aftermath"

一些在全部部署镜像后发现，因此原镜像没有处理的问题：

- 如果无法连接到外部网络的网络已经配置了，安装器可能会卡住
- 开启自动登录的情况下 DISPLAY 可能是 :0 而不是 :1（有些硬编码 `DISPLAY` 的地方需要修改，rootfs 中已经处理了）
- 无线网络下同时 SSH 数百台设备可能是不可靠的——批量 SSH 的脚本一定要考虑加入重试以及 `set -eo pipefail`
- 设置 `SUBMITCONTEST` 是没有必要的，因为只有一场比赛，而且热身赛和正赛的名字不一样
- 搞个截屏或者录屏的基础设施（从裁判室到场地有一些距离）
    - `xwd` 可以实现截图，但是**存在一个 bug：比赛时发现部分机器的屏幕无法截图，显示 `X Error of failed request:  BadColor (invalid Colormap parameter)` 错误**。怀疑是有窗口的 colormap 没有被对应程序正确设置。如果需要可靠截图，可能需要考虑另寻方案。

### 流程（回忆版本）

检查 hostname 和实际是否一致——批量执行（环境变量视情况修改）：

```bash
DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority zenity --info --text "<span font='128'>$(hostname)</span>"
```

会以超大字号弹窗显示 hostname。

现场调试完成后：

1. （热身赛开始前、结束后）删除 `icpc2023` 用户，新建 `icpc` 用户，设置自动登录关闭。
2. （热身赛结束后）重启后执行 `systemd-tmpfiles --clean` 清理临时目录，并检查 `/tmp` 与 `/var/tmp` 是否包含多余的文件。
2. （热身赛）推送 `合肥选手须知.pdf` 至 `/tmp` 再移动到 `/home/icpc/Desktop`。检查文件 SHA256 一致性。
3. （Both）开赛前一分钟对所有机器执行 `/opt/set-autologin`。
4. （Both）比赛结束后对所有机器执行 `/opt/set-nologin`。
    - 正式赛由于评测机在比赛开始阶段的故障，以及大量的重判导致的评测积压，实际到了 10min 等待选手的 clarification + 全部评测结束再执行这个脚本。

### 关于选手机，最常见的问题

1. 如何打开 IDE/编辑器/编译器（点击屏幕左上角 Applications 然后点 Programming，**最好能写到选手须知里头**）。
    - 环境事实上是 GNOME Flashback，只用过 Ubuntu 自带的默认 GNOME Shell 的人可能会有点不适应，只用过 Windows 话可能更不适应。
2. 如何调整屏幕亮度（Flashback 没这个 slider，但是我们的一体机可以硬件按钮调）。
3. 自己锁屏/注销（换语言）/重启然后被锁在外面了（`loginctl unlock-sessions` 可以解锁，如果 tty 不对 `chvt` 可以更换屏幕显示的 tty）。
4. VSCode 调试程序的时候弹窗关不掉（我也不知道为什么，但是按 ESC 就行了）。
5. Code::Blocks 卡住了（进终端杀进程）。
6. 我电脑卡了——一般我跑过去之后就好了，所以也不知道是什么导致的。

### 工具

参见 `tools` 文件夹。**从部署的 monitor 的 `/var/lib/icpc-monitor/state.json` 中获取机器列表的 JSON 会很有帮助**，包括但不限于：

- 你的脚本可以直接解析 JSON 获取全部有效 IP（DHCP 设置足够长的租约 / lease time 即可）；
- 你可以向 `/etc/hosts` 添加座位号和 IP 的对应关系，需要的时候就可以直接 `ssh root@A02` 了；

### Server Admin's "aftermath"

Disclaimer: 以下内容是服务器关机后当晚我基于当时的记录与回忆写的，因此不能排除存在偏差的可能性。以未来对日志分析完成后发布的官方结论为准。

**Update (2023/11/29): 周一晚对数据库的分析显示对 `Wall time >> CPU time` 问题，以下推论是错误的，导致错误推论的原因是调整 Wall time limit 上限与接网线的时间接近，导致错误判断问题已经解决。在模拟构建环境中相关问题可复现，并与 Linux kernel 中内存子系统与 cgroup 的实现有关。之后会更新详细的技术细节。**

周六的热身赛没有出现什么问题，但是周日的正赛出现了令人不满意的情况：

- 评测机的 ~~硬件~~ 内核问题导致一部分题目 Wall time >> CPU time 从而 TLE；
- DOMjudge 的默认配置问题导致倒数几分钟时出现了 \~50 秒的 502。

我相信以下两点：

- 我没有作为选手参加过 ACM 赛制比赛，因此我无法评价题目质量。但是据我在裁判室的观察，不管是科大的同学还是南京赛站来的运维同学，没有人在摆烂或者故意搞砸事情；
- 复盘并思考相关环节的问题是很有必要的——目的不是去指责某个人或者某一批人或者推脱责任，而是**避免相同的事情在其他赛站重演**。

所以从非选手的视角的一些观察：

- 周六的热身赛没有实质起到压力测试的作用，题目的难度、测试点等和正赛的分布完全不同，导致问题完全没有在热身赛暴露出来；
- 正赛签到题最开始的测试点过多，导致评测机堆积了大量的评测任务；
- 在配置从南京运来的机器的时候没有关注机器的 `dmesg`，发现评测机的空网口在不停（跟不存在的网线）重复协商速率的时候已经是发现大量评测误 TLE 的时候了；
    - ~~在发现这个问题后也没有办法确认就是内核驱动在不停重试导致的问题，最开始的时候怀疑是 systemd-journald 处理大量日志导致的，在关闭其 kmsg 记录并且 rate limit 之后问题依然存在，才想到插假网线的 workaround。~~
    - 这个问题的特征明确是 Wall time >> CPU time，因此没有重测 CPU time 就已经超时的提交。
    - DOMjudge UI 对这种重测需求很不友好，因此现场实际上是一个一个检查了所有的 TLE 提交，并且手工对全部符合条件的提交重测。不过之后的 clarification 中所有要求再重测的队伍都进行了检查（我记得应该都不满足这个条件因此没有重测？）。
- DOMjudge 的配置文档对 `pm.max_children` 需要根据内存大小修改的说明含糊不清（和南京站一样，默认值只有 40！），导致配置时很容易出现疏忽，并且这个问题**其他赛站也有很大概率存在**。
    - 相关默认配置：

        ```ini
        pm = static
        pm.max_children = 40      ; ~40 per gig of memory(16gb system -> 500)
        pm.max_requests = 5000
        pm.status_path = /fpm_status
        ```

        该配置**不会**被 DOMjudge 的配置检查器检查。
    - 502 期间没有有效的日志（只知道 `connect()` fpm 的 UNIX socket 收到了 `EAGAIN`），推测是 `pm.max_children` 过小 + 数据库访问较慢，然后请求堆积导致超过 `listen.backlog` 队列大小（Ubuntu php-fpm 默认看起来是 511）的请求被拒绝。`pm.max_requests` 设置的是 php-fpm 子进程重启前最多会处理的请求数量，因此与这个问题应当无关。

未来的运维/题目负责人需要注意什么？

- **一定要压测**。
    - 正赛的 F 题就是一个很好的例子，可以模拟许多选手同时提交，然后观察是否会出现非预期的 TLE。
    - 对比 CPU time 和 Wall time，观察是否出现了 Wall time >> CPU time 的情况。
    - DOMjudge 最简单的压测（1000 并发，视情况增减）：`siege --no-follow --concurrent=1000 -t30S -b --no-parser http://192.168.99.2/domjudge/public`.
    - 如果可以的话，考虑如何让热身赛起到压测的效果。
- 不要让简单题的评测花太长时间。
- 考虑 Nginx 设置分 IP 限流（每个选手的 IP 不同）。
- 数据库通常是瓶颈（可以查看 DOMjudge 慢日志），因此可以考虑扩大数据库的内存。本次比赛的数据库不到 4G，对于一台 dedicated web server 来说全部缓存都没问题。
- 数据库开启慢查询日志（至少有更多的机会知道是 DOMjudge 哪里出问题了）。
