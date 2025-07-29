/**
 * Router.js - Single Page Application Navigation Handler
 * Cấu trúc module dễ mở rộng cho nhiều route
 */

const Router = {
  // Cấu hình các route
  routes: [
    {
      path: '/home',
      elementId: 'home-logo'
    },
    {
      path: '/category',
      elementId: 'category-link'
    },
    {
      path: '/movies',
      elementId: 'detail-movie'
    },
    {
      path: '/profile',
      elementId: 'userIcon'
      
    }

    // Thêm route mới vào đây
  ],

  // Khởi tạo router
  init() {
    this.setupEventListeners();
    console.log('Router initialized');
  },

  // Thiết lập event listeners cho tất cả route
setupEventListeners() {
  this.routes.forEach(route => {
    const ids = Array.isArray(route.elementIds) ? route.elementIds : [route.elementIds];
    ids.forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        element.addEventListener('click', (e) => this.navigate(e, route.path));
      } else {
        console.warn(`Element #${id} not found for route: ${route.path}`);
      }
    });
  });
},

  // Xử lý chuyển trang
  navigate(event, path) {
    event.preventDefault();

    // Kiểm tra nếu đang ở trang đích thì không làm gì
    if (window.location.pathname === path) {
      console.log(`Already at ${path}`);
      return;
    }

    console.log(`Navigating to: ${path}`);

    // Phiên bản nâng cao có thể dùng History API
    if (this.supportsHistoryAPI()) {
      history.pushState({}, '', path);
      this.loadContent(path);
    } else {
      // Fallback cho trình duyệt cũ
      window.location.href = path;
    }
  },

  // Tải nội dung bằng Fetch API (SPA)
  async loadContent(path) {
    try {
      const response = await fetch(path);
      if (!response.ok) throw new Error('Network response was not ok');

      const html = await response.text();
      document.getElementById("main-content").innerHTML = html;
      console.log(`Content loaded for: ${path}`);

      // Khởi tạo lại router sau khi tải nội dung mới
      this.init();
    } catch (error) {
      console.error('Failed to load content:', error);
      window.location.href = path; // Fallback
    }
  },

  // Kiểm tra hỗ trợ History API
  supportsHistoryAPI() {
    return window.history && typeof window.history.pushState === 'function';
  }
};

// Khởi động router khi DOM sẵn sàng
document.addEventListener('DOMContentLoaded', () => Router.init());

// Export cho module system (nếu cần)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = Router;
}
