const { createApp } = Vue;

createApp({
    data() {
        return {
            filters: {
                movieName: '',
                startDate: '',
                hall: '',
                state: ''
            },
            movieOptions: [],
            dateOptions: [],
            hallOptions: [],
            statusOptions: [
                { value: '0', label: '已完成' },
                { value: '1', label: '申请退票中' },
                { value: '2', label: '退票完成' }
            ],
            orders: [],
            currentPage: 1,
            pageSize: 10
        }
    },
    computed: {
        totalPages() {
            return Math.ceil(this.orders.length / this.pageSize);
        },
        currentPageOrders() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.orders.slice(start, end);
        }
    },
    mounted() {
        this.loadFilterOptions();
        this.loadAllOrders();
    },
    methods: {
        async loadFilterOptions() {
            try {
                const response = await fetch('/api/orders/filter-options');
                const result = await response.json();

                if (result.success) {
                    this.movieOptions = result.data.movieNames || [];
                    this.dateOptions = result.data.dates || [];
                    this.hallOptions = result.data.halls || [];
                } else {
                    console.error('加载筛选选项失败:', result.message);
                }
            } catch (error) {
                console.error('网络错误:', error);
            }
        },

        async loadAllOrders() {
            try {
                const response = await fetch('/api/orders/all');
                const result = await response.json();

                if (result.success) {
                    this.orders = result.data;
                    this.currentPage = 1;
                } else {
                    console.error('加载订单失败:', result.message);
                    this.orders = [];
                }
            } catch (error) {
                console.error('网络错误:', error);
                this.orders = [];
            }
        },

        async searchOrders() {
            try {
                const params = new URLSearchParams();
                if (this.filters.movieName) params.append('movie_name', this.filters.movieName);
                if (this.filters.startDate) params.append('start_date', this.filters.startDate);
                if (this.filters.hall) params.append('hall', this.filters.hall);
                if (this.filters.state) params.append('state', this.filters.state);

                const response = await fetch(`/api/orders/search?${params.toString()}`);
                const result = await response.json();

                if (result.success) {
                    this.orders = result.data;
                    this.currentPage = 1;
                } else {
                    console.error('搜索订单失败:', result.message);
                    this.orders = [];
                }
            } catch (error) {
                console.error('网络错误:', error);
                this.orders = [];
            }
        },

        // 检查日期是否在可用日期列表中（仅用于显示提示，不限制选择）
        isDateAvailable(date) {
            return this.dateOptions.includes(date);
        },

        // 分页方法
        changePage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
            }
        },

        // 状态显示方法
        getStatusText(state) {
            switch(state) {
                case 0: return '已完成';
                case 1: return '申请退票中';
                case 2: return '退票完成';
                default: return '未知状态';
            }
        },

        getStatusClass(state) {
            switch(state) {
                case 0: return 'status-completed';
                case 1: return 'status-refunding';
                case 2: return 'status-refunded';
                default: return '';
            }
        },

        formatDateTime(datetimeStr) {
            if (!datetimeStr) return '';
            const date = new Date(datetimeStr);
            return date.toLocaleString('zh-CN');
        },

        processRefund(orderId) {
            // 后续实现退票处理功能
            alert(`处理订单 ${orderId} 的退票申请`);
        }
    }
}).mount('#app');