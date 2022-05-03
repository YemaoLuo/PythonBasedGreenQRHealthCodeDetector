## /MacauQRCodeDetecAPI
```text
API for MacauQRCodeDetec
```
#### 公共Header参数
参数名 | 示例值 | 参数描述
--- | --- | ---
暂无参数
#### 公共Query参数
参数名 | 示例值 | 参数描述
--- | --- | ---
暂无参数
#### 公共Body参数
参数名 | 示例值 | 参数描述
--- | --- | ---
暂无参数
#### 预执行脚本
```javascript
暂无预执行脚本
```
#### 后执行脚本
```javascript
暂无后执行脚本
```
## /MacauQRCodeDetecAPI/run4det
```text
## This interface is used to implement the detection function

## 此接口用于实现检测功能
```
#### 接口状态
> 已完成

#### 接口URL
> http://localhost:8000/run4det

#### 请求方式
> POST

#### Content-Type
> form-data

#### 请求Body参数
参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
uploadFile | C:\Users\Yemao Luo\Desktop\testImg_Fail.jpg | File | 是 | Img for detection
#### 预执行脚本
```javascript
暂无预执行脚本
```
#### 后执行脚本
```javascript
暂无后执行脚本
```
#### 成功响应示例
```javascript
{
	"confidence": "0.9159056544303894",
	"start_point": "(310, 709)",
	"end_point": "(774, 1177)",
	"time": "0.22400188446044922s"
}
```
#### 错误响应示例
```javascript
{
	"flag": false
}
```
## /MacauQRCodeDetecAPI/run4ocr
```text
## This interface is used to implement the detection and OCR function

## 此接口用于实现检测和OCR功能
```
#### 接口状态
> 已完成

#### 接口URL
> http://localhost:8000/run4ocr

#### 请求方式
> POST

#### Content-Type
> form-data

#### 请求Body参数
参数名 | 示例值 | 参数类型 | 是否必填 | 参数描述
--- | --- | --- | --- | ---
uploadFile | C:\Users\Yemao Luo\Desktop\testImg_Fail.jpg | File | 是 | Img for detection
#### 预执行脚本
```javascript
暂无预执行脚本
```
#### 后执行脚本
```javascript
暂无后执行脚本
```
#### 成功响应示例
```javascript
{
	"flag": true,
	"result_det": {
		"Conf": "0.7423779368400574",
		"S_Point": "[149, 530]",
		"E_Point": "[865, 1452]",
		"D_Time": "0.3859999179840088s"
	},
	"result_ocr": {
		"Name": "罗叶茂",
		"Sex": "男",
		"Exp": "2021/09/21",
		"Flag": true,
		"O_Time": "2.398998498916626s"
	}
}
```
#### 错误响应示例
```javascript
{
	"flag": false
}
```