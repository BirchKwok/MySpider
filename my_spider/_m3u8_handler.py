from ._common_config import *


def m3u8_downloader(url, file_name):
    """获取m3u8链接内容"""
    response = requests.get(url)
    m3u8_content = response.text

    key = None
    iv = None
    video_urls = []

    # 解析m3u8内容，获取加密密钥、初始化向量和视频链接
    for line in m3u8_content.split('\n'):
        if line.startswith('#EXT-X-KEY'):
            key_line = line.split(',', 1)[0]
            key_uri = key_line.split('URI=')[1].strip('"')
            key_response = requests.get(key_uri)
            key_content = key_response.content
            key = binascii.hexlify(key_content)
            iv_line = line.split('IV=')[1].strip('"')
            iv = binascii.hexlify(iv_line.encode())
        elif line.endswith('.ts'):
            video_urls.append(url.rsplit('/', 1)[0] + '/' + line)

    if len(video_urls) > 0:
        # 创建输出文件
        with open(file_name, 'wb') as output:
            # 下载和合并视频片段
            for video_url in tqdm(video_urls, total=len(video_urls)):
                response = requests.get(video_url)
                encrypted_data = response.content

                if key and iv:
                    # 解密视频片段
                    cipher = AES.new(binascii.unhexlify(key), AES.MODE_CBC, binascii.unhexlify(iv))
                    decrypted_data = cipher.decrypt(encrypted_data)
                    output.write(decrypted_data)
                else:
                    output.write(encrypted_data)

        print('Download successful!')
    else:
        print('Video link not found!')

