# 配置一个简单flask应用的安装文件
# 1.导入setuptools

from setuptools import setup, find_packages

# 2.编写setup()函数

setup(
    name="flaskr",  # 应用名
    version="1.0.0",  # 版本号
    packages=find_packages(),  # 包括在安装包内的Python包
    include_package_data=False,  # 启用清单文件MANIFEST.in
    zip_safe=False,  # 为了让Flask在安装时能够找到应用，需要设置zip_safe=False
    install_requires=[  # 安装依赖的其他包
        "flask",
    ],
)

