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
            selectedSeats: [],
            scheduleId: null
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
            if (this.selectedSeats.length === 0) return 'Not selected';
            return this.selectedSeats.map(seat => `Row ${seat.row} Seat ${seat.col}`).join(', ');
        }
    },
    mounted() {
        this.getCurrentUser();
        this.loadScheduleInfo();
        this.loadSeats();
    },
    methods: {
        async getCurrentUser() {
            try {
                const response = await fetch('/api/current-user');
                const result = await response.json();

                if (result.success) {
                    this.username = result.data.username;
                } else {
                    console.error('Failed to get user info:', result.message);
                    window.location.href = '/';
                }
            } catch (error) {
                console.error('Network error:', error);
                window.location.href = '/';
            }
        },

        async loadScheduleInfo() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const scheduleId = urlParams.get('schedule_id');
                this.scheduleId = scheduleId;

                if (!scheduleId) {
                    alert('Invalid schedule ID');
                    window.location.href = '/user-buy';
                    return;
                }

                const response = await fetch(`/api/schedules/${scheduleId}`);
                const result = await response.json();

                if (result.success) {
                    this.scheduleInfo = result.data;
                } else {
                    alert('Failed to load schedule info: ' + result.message);
                    window.location.href = '/user-buy';
                }
            } catch (error) {
                alert('Network error, please try again');
                window.location.href = '/user-buy';
            }
        },

        async loadSeats() {
            try {
                if (!this.scheduleId) return;

                const response = await fetch(`/api/seats?schedule_id=${this.scheduleId}`);
                const result = await response.json();

                if (result.success) {
                    this.initializeSeatMap(result.data);
                } else {
                    console.error('Failed to load seats:', result.message);
                }
            } catch (error) {
                console.error('Network error:', error);
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
                        selected: this.selectedSeats.some(s => s.row === i + 1 && s.col === j + 1)
                    });
                }
                this.seatMap.push(row);
            }
        },

        toggleSeat(seat) {
            if (seat.state !== 0) return;

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
            return date.toLocaleString();
        },

        async confirmPurchase() {
    if (this.selectedSeatsCount === 0) {
        alert('Please select seats first');
        return;
    }

    if (!confirm(`Confirm purchase of ${this.selectedSeatsCount} tickets for ${this.totalPrice}￥?`)) {
        return;
    }

    try {
        const orderData = {
            movie_name: this.scheduleInfo.movie_name,
            start_time: this.scheduleInfo.start_time,
            hall: this.scheduleInfo.hall,
            seat: this.selectedSeatsText,
            total_price: parseFloat(this.totalPrice),
            schedule_id: parseInt(this.scheduleId),
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
            alert(`Purchase successful for user ${result.data.username}!`);
            window.location.href = `/my-order`;
        } else {
            if (result.code === 'SEAT_UNAVAILABLE') {
                alert('Some seats are no longer available. Please select other seats.');
                this.selectedSeats = [];
                this.loadSeats();
            } else {
                alert('Purchase failed: ' + result.message);
            }
        }
    } catch (error) {
        console.error('Purchase error:', error);
        alert('Network error, please try again');
    }
}
    }
}).mount('#app');