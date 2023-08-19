# autoloading-backend
网页后端部分（python+flask+MySQL+gunicorn），使用docker打包&amp;部署

## 简单部署测试

```shell
docker build -t autoloading:test .
docker run --rm -it -p 8080:8080 autoloading:test
```