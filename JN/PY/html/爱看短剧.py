<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="utf-8" />
  <title>Catvod | 主页</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />
  <meta name="description" content="Catvod 提供简洁高效的 Tvbox 接口、GitHub 文件加速服务与美图壁纸服务。" />
  <meta name="keywords" content="Catvod, TVbox, GitHub 加速, 高清壁纸, 壁纸 API, 文件加速" />
  <meta name="robots" content="index,follow" />
  <meta name="theme-color" content="#0F7D00" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <link rel="stylesheet" href="/css/all.min.css" />
  <link rel="manifest" href="/manifest.json" />
  <link rel="icon" href="/icons/icon-192.png" />
  <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.5.2/css/all.min.css" rel="stylesheet" />
  <link rel="stylesheet" href="/css/main.css" />
</head>
<body>
  <div id="wrapper">
    <main id="main" role="main">
      <header>
        <div class="avatar">
          <img src="/image/avatar.jpg" alt="Catvod 头像" loading="lazy" />
        </div>
        <h1>Catvod.com</h1>
        <p>简简单单！</p>
      </header>
      <footer>
        <ul class="icons" role="list">
          <li><a href="https://tvbox.catvod.com/" title="Tvbox接口" aria-label="Tvbox接口" target="_blank" rel="noopener noreferrer"><i class="fas fa-tv"></i></a></li>
          <li><a href="https://github.catvod.com/" title="GitHub 文件加速" aria-label="GitHub 文件加速" target="_blank" rel="noopener noreferrer"><i class="fab fa-github"></i></a></li>
          <li><a href="https://imgs.catvod.com/" title="随机精美壁纸" aria-label="随机精美壁纸" target="_blank" rel="noopener noreferrer"><i class="fas fa-image"></i></a></li>
          <li><a href="https://img.catvod.com/" title="4K随机背景图片" aria-label="4K随机背景图片" target="_blank" rel="noopener noreferrer"><i class="fas fa-photo-video"></i></a></li>
          <li><a href="https://lives.catvod.com/" title="TXT/M3U 转换工具" aria-label="TXT/M3U 转换工具" target="_blank" rel="noopener noreferrer"><i class="fas fa-cogs"></i></a></li>
          <li><a href="https://www.catvod.com/jiaoliu" title="联系我们" aria-label="联系我们" target="_blank" rel="noopener noreferrer"><i class="fas fa-comments"></i></a></li>
        </ul>
      </footer>
    </main>
  </div>
  <footer id="footer" role="contentinfo">
    <p id="copyright"></p>
  </footer>
  <script src="/js/main.js"></script>
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service-worker.js')
        .catch(err => console.warn('Service Worker 注册失败:', err));
    }
  </script>
</body>
</html>
