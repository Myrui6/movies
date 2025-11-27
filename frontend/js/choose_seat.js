const { createApp } = Vue;

createApp({
    data() {
        return {
            username: '',
            scheduleInfo: {
                movie_name: '',
                start_time: '',
                hall: '',
                price: 0
            },
            seatMap: [],
            selectedSeats: []
        }
    },
    computed: {
        selectedSeatsCount() {
            return this.selectedSeats.length;
        },
        totalPrice() {
            return (this.selectedSeatsCount * this.scheduleInfo.price).toFixed(2);
        },
        selectedSeatsText() {
            if (this.selectedSeats.length === 0) return '未选择';
            return this.selectedSeats.map(seat => `${seat.row}排${seat.col}座`).join(', ');
        }
    },
    mounted() {
        this.getUsername();
        this.loadScheduleInfo();
        this.loadSeats();
    },
    methods: {
        getUsername() {
            const urlParams = new URLSearchParams(window.location.search);
            const username = urlParams.get('username');
            this.username = username || 'user';
        },

        async loadScheduleInfo() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const scheduleId = urlParams.get('schedule_id');

                if (!scheduleId) {
                    alert('无效的场次ID');
                    window.location.href = '/user-buy';
                    return;
                }

                const response = await fetch(`/api/schedules/${scheduleId}`);
                const result = await response.json();

                if (result.success) {
                    this.scheduleInfo = result.data;
                } else {
                    alert('加载场次信息失败：' + result.message);
                    window.location.href = '/user-buy';
                }
            } catch (error) {
                alert('网络错误，请重试');
                window.location.href = '/user-buy';
            }
        },

        async loadSeats() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const scheduleId = urlParams.get('schedule_id');

                if (!scheduleId) return;

                const response = await fetch(`/api/seats?schedule_id=${scheduleId}`);
                const result = await response.json();

                if (result.success) {
                    this.initializeSeatMap(result.data);
                } else {
                    console.error('加载座位失败:', result.message);
                }
            } catch (error) {
                console.error('网络错误:', error);
            }
        },

        initializeSeatMap(seatsData) {
            const rows = this.scheduleInfo.seat_rows;
            const cols = this.scheduleInfo.seat_columns;

            this.seatMap = [];
            for (let i = 0; i < rows; i++) {
                const row = [];
                for (let j = 0; j < cols; j++) {
                    const seat = seatsData.find(s => s.row_num === i + 1 && s.col_num === j + 1);
                    row.push({
                        row: i + 1,
                        col: j + 1,
                        state: seat ? seat.state : 0,
                        selected: false
                    });
                }
                this.seatMap.push(row);
            }
        },

        toggleSeat(seat) {
            if (seat.state === 1) return;

            seat.selected = !seat.selected;

            if (seat.selected) {
                this.selectedSeats.push({ row: seat.row, col: seat.col });
            } else {
                this.selectedSeats = this.selectedSeats.filter(
                    s => !(s.row === seat.row && s.col === seat.col)
                );
            }
        },

        formatDateTime(datetimeStr) {
            if (!datetimeStr) return '';
            const date = new Date(datetimeStr);
            return date.toLocaleString('zh-CN');
        },

        async confirmPurchase() {
            if (this.selectedSeatsCount === 0) {
                alert('请先选择座位');
                return;
            }

            try {
                const urlParams = new URLSearchParams(window.location.search);
                const scheduleId = urlParams.get('schedule_id');

                const orderData = {
                    username: this.username,
                    movie_name: this.scheduleInfo.movie_name,
                    start_time: this.scheduleInfo.start_time,
                    hall: this.scheduleInfo.hall,
                    seat: this.selectedSeatsText,
                    total_price: parseInt(this.totalPrice),
                    schedule_id: scheduleId,
                    selected_seats: this.selectedSeats
                };

                const response = await fetch('/api/orders', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(orderData)
                });

                const result = await response.json();

                if (result.success) {
                    alert('购票成功！');
                    window.location.href = `/my-order?username=${this.username}`;
                } else {
                    alert('购票失败：' + result.message);
                }
            } catch (error) {
                alert('网络错误，请重试');
            }
        }
    }
}).mount('#app');