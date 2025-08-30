// Основной объект приложения
const App = {
    currentPage: 'profile',
    userData: null,
    tasks: [],
    
    init() {
        console.log('App initialized');
        
        // Инициализация Telegram Web App
        this.tg = window.Telegram.WebApp;
        this.tg.expand();
        
        // Получаем данные пользователя из Telegram
        const initData = this.tg.initDataUnsafe;
        this.userId = initData.user?.id;
        
        if (!this.userId) {
            console.error('User ID not found');
            return;
        }
        
        // Загружаем данные пользователя
        this.loadUserData();
        
        // Назначаем обработчики событий
        this.setupEventListeners();
    },
    
    setupEventListeners() {
        document.getElementById('go-to-tasks').addEventListener('click', () => {
            this.showPage('tasks');
        });
        
        document.getElementById('back-to-profile').addEventListener('click', () => {
            this.showPage('profile');
        });
        
        document.getElementById('back-to-tasks').addEventListener('click', () => {
            this.showPage('tasks');
        });
    },
    
    async loadUserData() {
        try {
            // Здесь будет запрос к нашему API для получения данных пользователя
            // Временно используем заглушку
            this.userData = {
                name: 'Иван Иванов',
                keys: 3
            };
            
            this.updateProfile();
        } catch (error) {
            console.error('Error loading user data:', error);
        }
    },
    
    updateProfile() {
        document.getElementById('user-name').textContent = this.userData.name;
        document.getElementById('keys-count').textContent = this.userData.keys;
        
        // Показываем страницу с поздравлением, если все ключи собраны
        if (this.userData.keys >= 7) {
            this.showPage('congrats');
        }
    },
    
    showPage(pageName) {
        // Скрываем все страницы
        document.querySelectorAll('.page').forEach(page => {
            page.classList.add('hidden');
        });
        
        // Показываем нужную страницу
        document.getElementById(`${pageName}-page`).classList.remove('hidden');
        this.currentPage = pageName;
        
        // Загружаем данные для страницы, если необходимо
        if (pageName === 'tasks') {
            this.loadTasks();
        }
    },
    
    async loadTasks() {
        try {
            // Здесь будет запрос к API для получения заданий
            // Временно используем заглушку
            this.tasks = [
                { id: 1, name: 'Сентябрь', status: 'completed' },
                { id: 2, name: 'Октябрь', status: 'available' },
                { id: 3, name: 'Ноябрь', status: 'unavailable' },
                { id: 4, name: 'Декабрь', status: 'unavailable' },
                { id: 5, name: 'Январь', status: 'unavailable' },
                { id: 6, name: 'Февраль', status: 'unavailable' },
                { id: 7, name: 'Март', status: 'unavailable' }
            ];
            
            this.renderTasks();
        } catch (error) {
            console.error('Error loading tasks:', error);
        }
    },
    
    renderTasks() {
        const tasksList = document.getElementById('tasks-list');
        tasksList.innerHTML = '';
        
        this.tasks.forEach(task => {
            const taskElement = document.createElement('div');
            taskElement.className = 'task-item';
            taskElement.innerHTML = `
                <span>${task.name}</span>
                <span class="task-status status-${task.status}">${this.getStatusText(task.status)}</span>
            `;
            
            // Делаем задание кликабельным, если оно доступно
            if (task.status === 'available' || task.status === 'completed') {
                taskElement.style.cursor = 'pointer';
                taskElement.addEventListener('click', () => {
                    this.openTask(task);
                });
            }
            
            tasksList.appendChild(taskElement);
        });
    },
    
    getStatusText(status) {
        const statusMap = {
            'completed': 'Пройдено',
            'available': 'Доступно',
            'unavailable': 'Недоступно'
        };
        
        return statusMap[status] || status;
    },
    
    openTask(task) {
        if (task.status === 'available') {
            this.showPage('task-detail');
            document.getElementById('task-month').textContent = task.name;
            // Здесь будет логика загрузки и отображения задания
        } else if (task.status === 'completed') {
            alert('Это задание уже пройдено');
        }
    }
};

// Инициализируем приложение после загрузки DOM
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});