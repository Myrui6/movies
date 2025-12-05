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
                { value: '0', label: 'Completed' },
                { value: '1', label: 'Refund Requested' },
                { value: '2', label: 'Refunded' }
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
                    console.error('Failed to load filter options:', result.message);
                }
            } catch (error) {
                console.error('Network error:', error);
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
                    console.error('Failed to load orders:', result.message);
                    this.orders = [];
                }
            } catch (error) {
                console.error('Network error:', error);
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
                    console.error('Failed to search orders:', result.message);
                    this.orders = [];
                }
            } catch (error) {
                console.error('Network error:', error);
                this.orders = [];
            }
        },

        isDateAvailable(date) {
            return this.dateOptions.includes(date);
        },

        changePage(page) {
            if (page >= 1 && page <= this.totalPages) {
                this.currentPage = page;
            }
        },

        getStatusText(state) {
            switch(state) {
                case 0: return 'Completed';
                case 1: return 'Refund Requested';
                case 2: return 'Refunded';
                default: return 'Unknown Status';
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
            return date.toLocaleString();
        },

        async processRefund(orderId, reason) {
            const userChoice = confirm(`Refund reason: ${reason || 'No description'}\n\nPlease choose action:\nClick "OK" to approve refund\nClick "Cancel" to reject refund`);

            if (userChoice) {
                try {
                    const response = await fetch(`/api/orders/${orderId}/process-refund`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            action: 'approve'
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(result.message);
                        this.loadAllOrders();
                    } else {
                        alert('Operation failed: ' + result.message);
                    }
                } catch (error) {
                    console.error('Refund processing error:', error);
                    alert('Network error, please try again');
                }
            } else {
                try {
                    const response = await fetch(`/api/orders/${orderId}/process-refund`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            action: 'reject'
                        })
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(result.message);
                        this.loadAllOrders();
                    } else {
                        alert('Operation failed: ' + result.message);
                    }
                } catch (error) {
                    console.error('Refund processing error:', error);
                    alert('Network error, please try again');
                }
            }
        }
    }
}).mount('#app');