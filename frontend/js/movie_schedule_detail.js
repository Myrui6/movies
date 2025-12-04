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
            schedules: []
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
                const movieId = urlParams.get('id');

                if (!movieId) {
                    alert('无效的电影ID');
                    window.location.href = '/home';
                    return;
                }

                const response = await fetch(`/api/movies/${movieId}`);
                const result = await response.json();

                if (result.success) {
                    this.movie = result.data;
                } else {
                    alert('加载影片详情失败：' + result.message);
                    window.location.href = '/home';
                }
            } catch (error) {
                alert('网络错误，请重试');
                window.location.href = '/home';
            }
        },

        async loadSchedules() {
            try {
                const urlParams = new URLSearchParams(window.location.search);
                const movieId = urlParams.get('id');

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

        addSchedule() {
            const urlParams = new URLSearchParams(window.location.search);
            const movieId = urlParams.get('id');

            if (movieId && this.movie.name) {
                window.location.href = `/add-schedule?movie_id=${movieId}&movie_name=${encodeURIComponent(this.movie.name)}`;
            } else {
                alert('无法获取影片信息');
            }
        },

        formatDateTime(datetimeStr) {
            if (!datetimeStr) return '';
            const date = new Date(datetimeStr);
            return date.toLocaleString('zh-CN');
        },

        async deleteSchedule(scheduleId, movieName) {
            if (confirm(`确定要删除《${movieName}》的这个场次吗？\n\n注意：这将同时删除该场次的所有座位信息！`)) {
                try {
                    console.log('删除场次ID:', scheduleId);

                    const response = await fetch(`/api/schedules/${scheduleId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(result.message);
                        this.loadSchedules();
                    } else {
                        alert('删除失败：' + result.message);
                    }
                } catch (error) {
                    console.error('删除场次错误:', error);
                    alert('网络错误，请重试');
                }
            }
        }
    }
}).mount('#app');