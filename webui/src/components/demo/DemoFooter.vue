<template>
  <footer class="demo-footer">
    <div class="footer-inner">
      <div class="footer-brand">
        <span class="footer-logo-icon">M</span>
        <span class="footer-logo-text">OpenMOSS</span>
      </div>
      <p class="footer-desc">
        多 Agent 自组织协作平台 — 让 AI 像团队一样工作
      </p>
      <div class="footer-links">
        <a href="https://github.com/uluckyXH/OpenMOSS" target="_blank">GitHub</a>
        <span class="footer-dot">·</span>
        <a href="https://github.com/uluckyXH/OpenMOSS#quick-start" target="_blank">部署指南</a>
        <span class="footer-dot">·</span>
        <a href="https://1m-reviews.com" target="_blank">1M-Reviews</a>
        <span class="footer-dot">·</span>
        <a href="https://github.com/uluckyXH/OpenMOSS/issues" target="_blank">反馈</a>
      </div>
      <p class="footer-copy">MIT License · Built with ❤️</p>
    </div>
  </footer>
</template>

<style scoped>
.demo-footer {
  border-top: 1px solid #E8E6E0;
  background: #F5F4F0;
  margin-top: 48px;
}

.footer-inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 40px 32px;
  text-align: center;
}

.footer-brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 10px;
}

.footer-logo-icon {
  width: 20px;
  height: 20px;
  background: #1A1917;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Lora', serif;
  font-size: 11px;
  font-weight: 700;
  color: #FAFAF8;
}

.footer-logo-text {
  font-family: 'Lora', serif;
  font-weight: 700;
  font-size: 14px;
  color: #1A1917;
  letter-spacing: -0.3px;
}

.footer-desc {
  font-size: 13.5px;
  color: #8C8A84;
  margin: 0 0 16px;
}

.footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.footer-links a {
  font-family: 'Instrument Sans', sans-serif;
  font-size: 13px;
  font-weight: 500;
  color: #4A4845;
  text-decoration: none;
  padding: 3px 6px;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}

.footer-links a:hover {
  background: #EEECEA;
  color: #1A1917;
}

.footer-dot {
  color: #D4D0C8;
  font-size: 12px;
}

.footer-copy {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 11.5px;
  color: #B8B5AF;
  margin: 0;
  letter-spacing: 0.3px;
}

@media (max-width: 640px) {
  .footer-inner {
    padding: 28px 20px 24px;
  }
}
</style>
