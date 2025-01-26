"""
ETCD 证书生成脚本。

@requirements: 
    cryptography; python_version >= '3.6'
@author: zhaowcheng@163.com
@changelog:
    2025-01-25(v0.1.0): 初版
"""

import os
import sys
import argparse
import datetime
import ipaddress

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import (Encoding, 
                                                          PrivateFormat,
                                                          NoEncryption,
                                                          load_pem_private_key)
from cryptography.x509 import (Name, 
                               NameAttribute, 
                               SubjectAlternativeName,
                               CertificateBuilder, 
                               Certificate,
                               BasicConstraints,
                               IPAddress,
                               load_pem_x509_certificate)
from cryptography.x509.oid import NameOID
from cryptography.x509 import random_serial_number


VERSION = '0.1.0'
NAMEATTRS = [
    NameAttribute(NameOID.COUNTRY_NAME, "CN"),
    NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "CQ"),
    NameAttribute(NameOID.LOCALITY_NAME, "YB"),
    NameAttribute(NameOID.ORGANIZATION_NAME, "BC"),
    NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "ZWC")
]


def printerr_and_exit(msg: str, rc: int = 1) -> None:
    """
    打印错误消息并退出。

    :param msg: 消息
    :param rc: 退出码。
    """
    print(f'ERROR: {msg}', file=sys.stderr)
    exit(rc)


def save_key(key: rsa.RSAPrivateKey, path: str) -> None:
    """
    保存私钥。

    :param key: 私钥。
    :param path: 保存路径。
    """
    with open(path, 'wb') as f:
        f.write(key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=NoEncryption()
        ))
    print(f'Saved: {path}')


def save_cert(cert: Certificate, path: str) -> None:
    """
    保存证书。

    :param cert: 证书。
    :param path: 保存路径。
    """
    with open(path, 'wb') as f:
        f.write(cert.public_bytes(Encoding.PEM))
    print(f'Saved: {path}')


def gen_root_cert(savedir: str, days: int) -> None:
    """
    生成根证书。

    :param savedir: 保存目录。
    :param days: 有效期（天）。
    """
    # 生成根私钥
    root_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 生成根证书的公钥
    root_public_key = root_private_key.public_key()

    # 生成根证书的主题
    subject = issuer = Name(NAMEATTRS + [NameAttribute(NameOID.COMMON_NAME, "CA")])

    # 生成根证书
    root_cert = CertificateBuilder(
    ).subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        root_public_key
    ).serial_number(
        random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
    ).add_extension(
        BasicConstraints(ca=True, path_length=None), critical=True
    ).sign(root_private_key, hashes.SHA256())

    # 保存
    save_key(root_private_key, os.path.join(savedir, 'root.key'))
    save_cert(root_cert, os.path.join(savedir, 'root.cert'))

def gen_client_cert(
    rootkey: str, 
    rootcert: str, 
    savedir: str, 
    days: int, 
    cn: str = ''
) -> None:
    """
    生成客户端证书。

    :param rootkey: 根私钥。
    :param rootcert: 根证书。
    :param savedir: 保存目录。
    :param days: 有效期（天）。
    :param cn: 用户名。
    """
    # 加载根私钥和证书
    with open(rootkey, 'rb') as f:
        root_private_key = load_pem_private_key(f.read(), None)
    with open(rootcert, 'rb') as f:
        root_cert = load_pem_x509_certificate(f.read())

    # 生成客户端私钥
    client_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 生成客户端证书的公钥
    client_public_key = client_private_key.public_key()

    # 生成客户端证书的主题
    if cn:
        subject = Name(NAMEATTRS + [NameAttribute(NameOID.COMMON_NAME, cn)])
    else:
        subject = Name(NAMEATTRS)

    # 生成客户端证书
    client_cert = CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        root_cert.subject
    ).public_key(
        client_public_key
    ).serial_number(
        random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
    ).sign(root_private_key, hashes.SHA256())

    # 保存
    save_key(client_private_key, os.path.join(savedir, 'client.key'))
    save_cert(client_cert, os.path.join(savedir, 'client.cert'))


def gen_server_cert(
    rootkey: str, 
    rootcert: str, 
    savedir: str, 
    days: int,
    ip: str
) -> None:
    """
    生成服务端证书。

    :param rootkey: 根私钥。
    :param rootcert: 根证书。
    :param savedir: 保存目录。
    :param days: 有效期（天）。
    :param ip: 服务端 ip。
    """
    # 加载根私钥和证书
    with open(rootkey, 'rb') as f:
        root_private_key = load_pem_private_key(f.read(), None)
    with open(rootcert, 'rb') as f:
        root_cert = load_pem_x509_certificate(f.read())

    # 生成服务器私钥
    server_private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # 生成服务器证书的公钥
    server_public_key = server_private_key.public_key()

    # 生成服务器证书的主题
    subject = Name(NAMEATTRS)

    # 生成服务器证书的扩展（包括 IP SAN）
    san = SubjectAlternativeName([
        IPAddress(ipaddress.IPv4Address('127.0.0.1')),
        IPAddress(ipaddress.IPv4Address(ip))
    ])

    # 生成服务器证书
    server_cert = CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        root_cert.subject
    ).public_key(
        server_public_key
    ).serial_number(
        random_serial_number()
    ).not_valid_before(
        datetime.datetime.now(datetime.timezone.utc)
    ).not_valid_after(
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
    ).add_extension(
        san, critical=False
    ).sign(root_private_key, hashes.SHA256())

    # 保存
    save_key(server_private_key, os.path.join(savedir, f'{ip}.key'))
    save_cert(server_cert, os.path.join(savedir, f'{ip}.cert'))


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器。
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--command', required=True, choices=['gen_root_cert', 'gen_client_cert', 'gen_server_cert'])
    parser.add_argument('-s', '--savedir', required=True, default='.', help='Save directory. [default: .]')
    parser.add_argument('-d', '--days', type=int,  default=3650, 
                        help='Certificate validity period. [default: 3650]')
    parser.add_argument('-n', '--cn', help='Common name(only used for gen_client_cert).')
    parser.add_argument('-k', '--root-key', required=('gen_client_cert' in sys.argv or 'gen_server_cert' in sys.argv),
                        help='Root private key.')
    parser.add_argument('-t', '--root-cert', required=('gen_client_cert' in sys.argv or 'gen_server_cert' in sys.argv),
                        help='Root certificate.')
    parser.add_argument('-i', '--ip', required=('gen_server_cert' in sys.argv),
                        help='Server IP.')
    parser.add_argument('-v', '--version', action='version', version=VERSION)
    return parser


def main() -> None:
    """
    入口函数。
    """
    parser = create_parser()
    args = parser.parse_args()
    if not os.path.exists(args.savedir):
        printerr_and_exit(f'Savedir `{args.savedir}` does not exist.')
    if args.command == 'gen_root_cert':
        gen_root_cert(args.savedir, args.days)
    elif args.command == 'gen_client_cert':
        gen_client_cert(args.root_key, args.root_cert, args.savedir, args.days, args.cn)
    elif args.command == 'gen_server_cert':
        gen_server_cert(args.root_key, args.root_cert, args.savedir, args.days, args.ip)


if __name__ == '__main__':
    main()
