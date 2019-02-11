### 介绍一下？
无需拥有服务器，点点鼠标就能上线一个研招网成绩查询的接口。

实质是通过腾讯云无服务器云函数，制作一个REST风格的接口，通过GET请求即可**查询研究生入学考试的初试成绩**。

### 特性
- [x] 自动识别验证码
- [x] 无需修改我的💩脚本
- [x] 支持Server酱

### 预览一下?

> 作者不会收集任何人的信息。代码是开源的，最好自行部署较为放心。

请求方式：GET

`
https://service-5ur64h8n-1251079053.ap-shanghai.apigateway.myqcloud.com/release/yanzhao?xm=姓名&id=身份证号&kh=准考证号
`

返回样例：JSON

`{"Code": 101, "Msg": "Score not released yet", "Request_id": "e43f5c16-2dde-11e9-93a2-5254005d5fdb"}`

### 如何部署？
你需要准备注册[腾讯云](https://console.cloud.tencent.com/scf)和[腾讯优图](https://open.youtu.qq.com/#/open)。

- 下载最新的[Release压缩包](https://github.com/6r6/yz/releases)
- [腾讯云SCF](https://console.cloud.tencent.com/scf)后台新建 > 空白函数 ，函数名请随意，运行环境选择Python36
- 执行方法填入`index.main_handler`
- 提交方法选择本地上传ZIP包，上传刚下载的ZIP包
- 环境变量请配置`app_id`、`secret_id`、`secret_key`，请在腾讯优图开放平台获取这三个值
- 保存
- 触发方式 > API网关触发 > 默认参数保存，获得一个公网的查询地址

---
