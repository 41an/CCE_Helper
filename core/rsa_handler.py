from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def is_valid_rsa_private_key(data):
    """
    验证RSA私钥是否合法（支持PEM或DER，字符串或bytes）
    """
    if isinstance(data, str):
        data = data.encode()

    try:
        key = serialization.load_pem_private_key(data, password=None, backend=default_backend())
    except ValueError:
        try:
            key = serialization.load_der_private_key(data, password=None, backend=default_backend())
        except Exception:
            return False

    return isinstance(key, rsa.RSAPrivateKey)


def is_valid_rsa_public_key(data):
    """
    验证RSA公钥是否合法（支持PEM或DER，字符串或bytes）
    """
    if isinstance(data, str):
        data = data.encode()

    try:
        key = serialization.load_pem_public_key(data, backend=default_backend())
    except ValueError:
        try:
            key = serialization.load_der_public_key(data, backend=default_backend())
        except Exception:
            return False

    return isinstance(key, rsa.RSAPublicKey)


def pkcs1_to_pkcs8(pkcs1_pem: bytes) -> bytes:
    """
    将 PKCS#1 PEM 私钥转为 PKCS#8 PEM 格式
    """
    private_key = serialization.load_pem_private_key(pkcs1_pem, password=None)
    pkcs8_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    return pkcs8_pem


def pkcs8_to_pkcs1(pkcs8_pem: bytes) -> bytes:
    """
    将 PKCS#8 PEM 私钥转为 PKCS#1 PEM 格式
    """
    private_key = serialization.load_pem_private_key(pkcs8_pem, password=None)
    pkcs1_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,  # 即 PKCS#1
        encryption_algorithm=serialization.NoEncryption()
    )
    return pkcs1_pem


def pkcs1_pub_to_spki(pkcs1_pem: bytes) -> bytes:
    """
    将 PKCS#1 公钥 PEM 转为 SubjectPublicKeyInfo (SPKI) 格式
    """
    public_key = serialization.load_pem_public_key(pkcs1_pem)
    spki_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return spki_pem


def spki_to_pkcs1_pub(spki_pem: bytes) -> bytes:
    """
    将 SPKI 公钥 PEM 转为 PKCS#1 格式（仅适用于 RSA）
    """
    public_key = serialization.load_pem_public_key(spki_pem)
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("仅支持 RSA 公钥转换")

    pkcs1_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    )
    return pkcs1_pem


def convert_private_key_auto(pem_data: bytes) -> bytes:
    """
    自动判断私钥格式并进行 PKCS#1 ⇄ PKCS#8 转换
    - 如果是 PKCS#1，则转换为 PKCS#8
    - 如果是 PKCS#8，则转换为 PKCS#1
    """
    if b"BEGIN RSA PRIVATE KEY" in pem_data:
        # PKCS#1 -> PKCS#8
        # print("Detected PKCS#1, converting to PKCS#8")
        return pkcs1_to_pkcs8(pem_data).decode("utf-8")
    elif b"BEGIN PRIVATE KEY" in pem_data:
        # PKCS#8 -> PKCS#1
        # print("Detected PKCS#8, converting to PKCS#1")
        return pkcs8_to_pkcs1(pem_data).decode("utf-8")
    else:
        raise ValueError("err,无法识别的私钥格式，缺少标识头")


def convert_public_key_auto(pem_data: bytes) -> bytes:
    """
    自动判断公钥格式并进行 PKCS#1 ⇄ SPKI 转换
    - 如果是 PKCS#1，则转换为 SPKI
    - 如果是 SPKI，则转换为 PKCS#1
    """
    if b"BEGIN RSA PUBLIC KEY" in pem_data:
        # PKCS#1 -> SPKI
        print("Detected PKCS#1 public key, converting to SPKI")
        return pkcs1_pub_to_spki(pem_data)
    elif b"BEGIN PUBLIC KEY" in pem_data:
        # SPKI -> PKCS#1
        print("Detected SPKI public key, converting to PKCS#1")
        return spki_to_pkcs1_pub(pem_data)
    else:
        raise ValueError("无法识别的公钥格式，缺少标识头")


def extract_public_key_from_private(pem_private_key: bytes, password: bytes = None) -> bytes:
    """
    从 PEM 格式的 RSA 私钥中提取对应的公钥（PEM 格式）

    :param pem_private_key: PEM 格式的私钥字节串
    :param password: 如果私钥有加密，传入密码（bytes 类型），否则为 None
    :return: PEM 格式的公钥字节串
    """
    try:
        private_key = serialization.load_pem_private_key(pem_private_key, password=password)
        if not isinstance(private_key, rsa.RSAPrivateKey):
            raise ValueError("不是有效的 RSA 私钥")

        public_key = private_key.public_key()

        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem_public
    except Exception as e:
        raise ValueError(f"提取公钥失败: {e}")


class RSAUtil:
    def __init__(self, private_key=None, public_key=None, key_size=2048, public_exponent=65537):
        """
        初始化，生成RSA密钥对
        """
        if private_key:
            self.private_key = private_key
            self.public_key = private_key.public_key()
        elif public_key:
            self.private_key = None
            self.public_key = public_key
        else:
            self.private_key = rsa.generate_private_key(
                public_exponent=public_exponent,
                key_size=key_size
            )
            self.public_key = self.private_key.public_key()

    @staticmethod
    def load_private_key(data: bytes, password: bytes = None):
        """
        从PEM/DER数据加载私钥
        """
        return serialization.load_pem_private_key(data, password=password)

    @staticmethod
    def load_public_key(data: bytes):
        """
        从PEM/DER数据加载公钥
        """
        return serialization.load_pem_public_key(data)

    @classmethod
    def from_pem(cls, pem_bytes: bytes, password: bytes = None):
        try:
            # 尝试加载私钥
            private_key = serialization.load_pem_private_key(pem_bytes, password=password)
            return cls(private_key=private_key)
        except ValueError:
            # 如果无法解析为私钥，则尝试解析为公钥
            try:
                public_key = serialization.load_pem_public_key(pem_bytes)
                return cls(public_key=public_key)
            except Exception as e:
                raise ValueError("无法加载 PEM 密钥，既不是合法私钥也不是合法公钥") from e

    def export_private_key(self, encoding='PEM', format='PKCS8', password: bytes = None) -> bytes:
        """
        导出私钥

        encoding: 'PEM' 或 'DER'
        format: 'PKCS1' 或 'PKCS8'
        password: 加密私钥密码，为 None 时不加密
        """
        enc = serialization.Encoding.PEM if encoding.upper() == 'PEM' else serialization.Encoding.DER
        fmt = serialization.PrivateFormat.TraditionalOpenSSL if format.upper() == 'PKCS1' else serialization.PrivateFormat.PKCS8
        if password:
            encryption_alg = serialization.BestAvailableEncryption(password)
        else:
            encryption_alg = serialization.NoEncryption()

        return self.private_key.private_bytes(
            encoding=enc,
            format=fmt,
            encryption_algorithm=encryption_alg
        )

    def export_public_key(self, encoding='PEM') -> bytes:
        """
        导出公钥，encoding: 'PEM' 或 'DER'
        """
        enc = serialization.Encoding.PEM if encoding.upper() == 'PEM' else serialization.Encoding.DER
        return self.public_key.public_bytes(
            encoding=enc,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def sign(self, message: bytes, padding_mode='PSS', hash_alg='SHA256') -> bytes:
        """
        签名接口

        padding_mode: 'PSS' 或 'PKCS1v15'
        hash_alg: 'SHA256', 'SHA384', 'SHA512', 'SHA1' 等

        返回签名bytes
        """
        hash_algo = getattr(hashes, hash_alg.upper())()

        if padding_mode.upper() == 'PSS':
            pad = padding.PSS(
                mgf=padding.MGF1(hash_algo),
                salt_length=padding.PSS.MAX_LENGTH
            )
        elif padding_mode.upper() == 'PKCS1V15':
            pad = padding.PKCS1v15()
        else:
            raise ValueError(f"Unsupported padding_mode: {padding_mode}")

        return self.private_key.sign(
            message,
            pad,
            hash_algo
        )

    def verify(self, message: bytes, signature: bytes, padding_mode='PSS', hash_alg='SHA256') -> bool:
        """
        验签接口

        padding_mode: 'PSS' 或 'PKCS1v15'
        hash_alg: 'SHA256', 'SHA384', 'SHA512', 'SHA1' 等

        返回bool
        """
        hash_algo = getattr(hashes, hash_alg.upper())()

        if padding_mode.upper() == 'PSS':
            pad = padding.PSS(
                mgf=padding.MGF1(hash_algo),
                salt_length=padding.PSS.MAX_LENGTH
            )
        elif padding_mode.upper() == 'PKCS1V15':
            pad = padding.PKCS1v15()
        else:
            raise ValueError(f"Unsupported padding_mode: {padding_mode}")

        try:
            self.public_key.verify(
                signature,
                message,
                pad,
                hash_algo
            )
            return True
        except InvalidSignature:
            return False
