# 502 analysis

## tl;dr

- 502 错误比赛中多次出现；
- 14:28:53 - 14:29:32 有一个队伍访问了 1001 次（但是排除这个特例，大头恐怕还是 judgehost）；
- 关于慢日志，比较频繁的是 Symfony 的 `session_start()`。Session 如果能做成放进 redis 之类的内存数据库可能会好很多，但是需要改 `/opt/domjudge/domserver/webapp/config/packages/framework.yaml`，此外几乎所有慢日志都卡在了数据库上面，思考数据库调优可能是有必要的；
- 当然没有数据库慢日志，所以不知道具体是什么请求导致的。

## 日志信息整理

502 错误比赛中多次出现：12:05:00 - 12:05:01, 12:14:47 - 12:14:54, 14:28:00 - 14:28:10, 14:28:46 - 14:28:48, 14:28:53 - 14:29:32, 14:29:56 - 14:30:04, 14:30:08（仅一个请求）

14:29:31 重启了 PHP-FPM:

```
Nov 26 14:29:31 domserver systemd[1]: Stopping The PHP 8.1 FastCGI Process Manager...
```

数据库报错显示此时有 48 条连接断开：

```
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597048 [Warning] Aborted connection 2597048 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597050 [Warning] Aborted connection 2597050 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597063 [Warning] Aborted connection 2597063 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597062 [Warning] Aborted connection 2597062 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597060 [Warning] Aborted connection 2597060 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597059 [Warning] Aborted connection 2597059 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596899 [Warning] Aborted connection 2596899 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597061 [Warning] Aborted connection 2597061 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596902 [Warning] Aborted connection 2596902 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597022 [Warning] Aborted connection 2597022 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596879 [Warning] Aborted connection 2596879 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596938 [Warning] Aborted connection 2596938 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596810 [Warning] Aborted connection 2596810 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596906 [Warning] Aborted connection 2596906 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596828 [Warning] Aborted connection 2596828 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596911 [Warning] Aborted connection 2596911 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597047 [Warning] Aborted connection 2597047 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597049 [Warning] Aborted connection 2597049 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596915 [Warning] Aborted connection 2596915 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596922 [Warning] Aborted connection 2596922 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596925 [Warning] Aborted connection 2596925 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596935 [Warning] Aborted connection 2596935 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596937 [Warning] Aborted connection 2596937 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596939 [Warning] Aborted connection 2596939 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596944 [Warning] Aborted connection 2596944 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596956 [Warning] Aborted connection 2596956 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596959 [Warning] Aborted connection 2596959 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596964 [Warning] Aborted connection 2596964 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596971 [Warning] Aborted connection 2596971 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596975 [Warning] Aborted connection 2596975 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596993 [Warning] Aborted connection 2596993 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596995 [Warning] Aborted connection 2596995 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596998 [Warning] Aborted connection 2596998 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597006 [Warning] Aborted connection 2597006 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596946 [Warning] Aborted connection 2596946 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597014 [Warning] Aborted connection 2597014 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2596947 [Warning] Aborted connection 2596947 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597016 [Warning] Aborted connection 2597016 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597019 [Warning] Aborted connection 2597019 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597024 [Warning] Aborted connection 2597024 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597032 [Warning] Aborted connection 2597032 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597036 [Warning] Aborted connection 2597036 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597039 [Warning] Aborted connection 2597039 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597041 [Warning] Aborted connection 2597041 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597043 [Warning] Aborted connection 2597043 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597051 [Warning] Aborted connection 2597051 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 2597058 [Warning] Aborted connection 2597058 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error writing communication packets)
Nov 26 14:29:32 domserver mariadbd[1550]: 2023-11-26 14:29:32 1632436 [Warning] Aborted connection 1632436 to db: 'domjudge' user: 'domjudge' host: 'localhost' (Got an error reading communication packets)
```

14:29:32 重启成功：

```
Nov 26 14:29:32 domserver systemd[1]: Started The PHP 8.1 FastCGI Process Manager.
```

在比赛结束后的 14:30:04 又进行了一次重启：

```
Nov 26 14:30:04 domserver systemd[1]: Stopping The PHP 8.1 FastCGI Process Manager...
```

数据库同样有 48 条连接断开。

14:30:04 重启成功，14:30:05，两个 php-fpm 进程发生段错误：

```text
Nov 26 14:30:04 domserver systemd[1]: Started The PHP 8.1 FastCGI Process Manager.
Nov 26 14:30:05 domserver kernel: [159350.274705] php-fpm8.1[123301]: segfault at 55ca8f22ff78 ip 000055c20f52fc70 sp 00007ffc9d5bb570 error 4 in php-fpm8.1[55c20f324000+2f6000]
Nov 26 14:30:05 domserver kernel: [159350.274719] Code: 55 48 89 f5 53 48 8b 46 08 48 89 fb 48 85 c0 74 61 0b 43 0c 4c 8b 63 10 48 98 41 8b 1c 84 83 fb ff 74 77 48 c1 e3 05 4c 01 e3 <48> 3b 6b 18 75 32 48 89 d8 5b 5d 41 5c c3 66 90 48 8b 7b 18 48 85
Nov 26 14:30:05 domserver kernel: [159350.274746] php-fpm8.1[123282]: segfault at 55ca8f23aa08 ip 000055c20f52fc70 sp 00007ffc9d5bb570 error 4 in php-fpm8.1[55c20f324000+2f6000]
Nov 26 14:30:05 domserver kernel: [159350.274758] Code: 55 48 89 f5 53 48 8b 46 08 48 89 fb 48 85 c0 74 61 0b 43 0c 4c 8b 63 10 48 98 41 8b 1c 84 83 fb ff 74 77 48 c1 e3 05 4c 01 e3 <48> 3b 6b 18 75 32 48 89 d8 5b 5d 41 5c c3 66 90 48 8b 7b 18 48 85
```

## 请求分布

主要分析 nginx 的 domjudge-api 与 domjudge 两个 access log 文件。日志不含请求到响应所用的时间（仅包含精确到秒的日志记录时间，约等于响应时间），因此该项无法分析。

**以下仅对 14:28:53 - 14:29:32（第五次 502）这段时间最长、影响最大的进行分析**。在此时段（39s）中，超过 100 次访问的有：

- team12xx 访问了 1001 次，其中有 588 次 502，410 次客户端在响应前断开连接（499）。从日志来看，可能是不停按住了浏览器的 F5 键。
- judgehost 访问了 560 次，其中有 401 次 502，158 次 200。

最频繁的请求（次数 500+499+200）：

- GET /domjudge/team HTTP/1.1 (1248+668+77)
- GET /domjudge/team/problems HTTP/1.1 (226+129+8)
- GET /domjudge/team/scoreboard HTTP/1.1 (184+53+15)
- GET /domjudge/ HTTP/1.1 (90+53+0，5 个 302)
- POST /domjudge/api/judgehosts/fetch-work HTTP/1.1 (49+0+29)

其中与提交相关的请求为 `POST /domjudge/team/submit HTTP/1.1`，合计 502 22 次，499 5 次，302 5 次。

## Domjudge (PHP) 慢日志分析

从 14:28:25 开始出现了大量慢日志。其中 64 条的内容是（与数据库操作和 Symfony Session 有关）：

```
script_filename = /opt/domjudge/domserver/webapp/public/index.php
execute() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Storage/Handler/PdoSessionHandler.php:667
doRead() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Storage/Handler/AbstractSessionHandler.php:99
read() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Storage/Handler/PdoSessionHandler.php:300
read() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Storage/Handler/AbstractSessionHandler.php:66
validateId() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Storage/Proxy/SessionHandlerProxy.php:100
validateId() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Storage/NativeSessionStorage.php:185
session_start() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Storage/NativeSessionStorage.php:185
start() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Storage/NativeSessionStorage.php:352
getBag() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Session.php:261
getBag() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Session.php:283
getAttributeBag() /opt/domjudge/domserver/lib/vendor/symfony/http-foundation/Session/Session.php:77
get() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall/ContextListener.php:106
authenticate() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall/AbstractListener.php:26
__invoke() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall.php:119
callListeners() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall.php:92
onKernelRequest() /opt/domjudge/domserver/lib/vendor/symfony/event-dispatcher/EventDispatcher.php:270
Symfony\Component\EventDispatcher\{closure}() /opt/domjudge/domserver/lib/vendor/symfony/event-dispatcher/EventDispatcher.php:230
callListeners() /opt/domjudge/domserver/lib/vendor/symfony/event-dispatcher/EventDispatcher.php:59
dispatch() /opt/domjudge/domserver/lib/vendor/symfony/http-kernel/HttpKernel.php:139
handleRaw() /opt/domjudge/domserver/lib/vendor/symfony/http-kernel/HttpKernel.php:75
```

7 条内容是（与数据库操作和 `getGroupedProblemsStats` 有关）：

```
script_filename = /opt/domjudge/domserver/webapp/public/index.php
execute() /opt/domjudge/domserver/lib/vendor/doctrine/dbal/src/Driver/PDO/Statement.php:134
execute() /opt/domjudge/domserver/lib/vendor/sentry/sentry-symfony/src/Tracing/Doctrine/DBAL/AbstractTracingStatement.php:77
traceFunction() /opt/domjudge/domserver/lib/vendor/sentry/sentry-symfony/src/Tracing/Doctrine/DBAL/TracingStatementForV3.php:43
execute() /opt/domjudge/domserver/lib/vendor/doctrine/dbal/src/Connection.php:1062
executeQuery() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/Query/Exec/SingleSelectExecutor.php:31
execute() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/Query.php:325
_doExecute() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/AbstractQuery.php:1212
executeIgnoreQueryCache() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/AbstractQuery.php:1166
execute() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/AbstractQuery.php:913
getArrayResult() /opt/domjudge/domserver/webapp/src/Service/StatisticsService.php:484
getGroupedProblemsStats() /opt/domjudge/domserver/webapp/src/Service/DOMJudgeService.php:986
getTwigDataForProblemsAction() /opt/domjudge/domserver/webapp/src/Controller/Team/ProblemController.php:57
problemsAction() /opt/domjudge/domserver/lib/vendor/symfony/http-kernel/HttpKernel.php:163
handleRaw() /opt/domjudge/domserver/lib/vendor/symfony/http-kernel/HttpKernel.php:75
handle() /opt/domjudge/domserver/lib/vendor/symfony/http-kernel/Kernel.php:202
handle() /opt/domjudge/domserver/webapp/public/index.php:28
```

比赛结束前另外两条为：

（数据库操作与 Symfony 用户认证）

```
script_filename = /opt/domjudge/domserver/webapp/public/index.php
execute() /opt/domjudge/domserver/lib/vendor/doctrine/dbal/src/Driver/PDO/Statement.php:134
execute() /opt/domjudge/domserver/lib/vendor/sentry/sentry-symfony/src/Tracing/Doctrine/DBAL/AbstractTracingStatement.php:77
traceFunction() /opt/domjudge/domserver/lib/vendor/sentry/sentry-symfony/src/Tracing/Doctrine/DBAL/TracingStatementForV3.php:43
execute() /opt/domjudge/domserver/lib/vendor/doctrine/dbal/src/Connection.php:1062
executeQuery() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/Persisters/Entity/BasicEntityPersister.php:750
load() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/Persisters/Entity/BasicEntityPersister.php:768
loadById() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/EntityManager.php:521
find() /opt/domjudge/domserver/lib/vendor/doctrine/orm/lib/Doctrine/ORM/EntityRepository.php:197
find() /opt/domjudge/domserver/lib/vendor/symfony/doctrine-bridge/Security/User/EntityUserProvider.php:111
refreshUser() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall/ContextListener.php:236
refreshUser() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall/ContextListener.php:137
authenticate() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall/AbstractListener.php:26
__invoke() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall.php:119
callListeners() /opt/domjudge/domserver/lib/vendor/symfony/security-http/Firewall.php:92
onKernelRequest() /opt/domjudge/domserver/lib/vendor/symfony/event-dispatcher/EventDispatcher.php:270
Symfony\Component\EventDispatcher\{closure}() /opt/domjudge/domserver/lib/vendor/symfony/event-dispatcher/EventDispatcher.php:230
callListeners() /opt/domjudge/domserver/lib/vendor/symfony/event-dispatcher/EventDispatcher.php:59
dispatch() /opt/domjudge/domserver/lib/vendor/symfony/http-kernel/HttpKernel.php:139
handleRaw() /opt/domjudge/domserver/lib/vendor/symfony/http-kernel/HttpKernel.php:75
handle() /opt/domjudge/domserver/lib/vendor/symfony/http-kernel/Kernel.php:202
```

（与 Twig 模板渲染有关）

```
script_filename = /opt/domjudge/domserver/webapp/public/index.php
doDisplay() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:394
displayWithErrorHandling() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:367
display() /opt/domjudge/domserver/webapp/var/cache/prod/twig/da/dabe30dd67ad7967d821bc245b44244a.php:78
block_content() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:171
displayBlock() /opt/domjudge/domserver/webapp/var/cache/prod/twig/bb/bbfdaa9ae37606d3eb311329752e614d.php:272
block_body() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:171
displayBlock() /opt/domjudge/domserver/webapp/var/cache/prod/twig/bb/bbfdaa9ae37606d3eb311329752e614d.php:133
doDisplay() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:394
displayWithErrorHandling() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:367
display() /opt/domjudge/domserver/webapp/var/cache/prod/twig/70/703094972463f848bf989985a9910816.php:47
doDisplay() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:394
displayWithErrorHandling() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:367
display() /opt/domjudge/domserver/webapp/var/cache/prod/twig/da/dabe30dd67ad7967d821bc245b44244a.php:46
doDisplay() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:394
displayWithErrorHandling() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:367
display() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Template.php:379
render() /opt/domjudge/domserver/lib/vendor/twig/twig/src/TemplateWrapper.php:40
render() /opt/domjudge/domserver/lib/vendor/twig/twig/src/Environment.php:280
render() /opt/domjudge/domserver/lib/vendor/symfony/framework-bundle/Controller/AbstractController.php:258
renderView() /opt/domjudge/domserver/lib/vendor/symfony/framework-bundle/Controller/AbstractController.php:266
```
