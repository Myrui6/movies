const { createApp } = Vue;

createApp({
    data() {
        return {
            movie: {
                name: '',
                picture: '',
                type: '',
                region: '',
                time: '',
                brief: ''
            },
            schedules: [],
            username: 'user' // 从登录信息获取，暂时写死为 'user'
        }
    },
    mounted() {
        this.loadMovieDetail();
        this.loadSchedules();
    },
    methods: {
        async loadMovieDetail() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const movieId = urlParams.get('movie_id');

                if (!movieId) {
                    alert('无效的电影ID');
                    window.location.href = '/user-buy';
                    return;
                }

                const response = await fetch(`/api/movies/${movieId}`);
                const result = await response.json();

                if (result.success) {
                    this.movie = result.data;
                } else {
                    alert('加载影片详情失败：' + result.message);
                    window.location.href = '/user-buy';
                }
            } catch (error) {
                alert('网络错误，请重试');
                window.location.href = '/user-buy';
            }
        },

        async loadSchedules() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const movieId = urlParams.get('movie_id');

                if (!movieId) return;

                // 修改这里：使用正确的API端点获取特定电影的场次
                const response = await fetch(`/api/schedules/movie/${movieId}`);
                const result = await response.json();

                if (result.success) {
                    this.schedules = result.data;
                } else {
                    console.error('加载场次失败:', result.message);
                    this.schedules = [];
                }
            } catch (error) {
                console.error('网络错误:', error);
                this.schedules = [];
            }
        },

        formatDateTime(datetimeStr) {
            if (!datetimeStr) return '';
            const date = new Date(datetimeStr);
            return date.toLocaleString('zh-CN');
        },

        chooseSeat(scheduleId) {
            window.location.href = `/choose-seat?schedule_id=${scheduleId}&username=${this.username}`;
        }
    }
}).mount('#app');