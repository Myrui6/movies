const { createApp } = Vue;

createApp({
    data() {
        return {
            halls: [],
            isAdding: false, // 控制行内添加表单是否显示
            newHall: {
                name: '',
                total_rows: 10, // 默认值
                total_columns: 15 // 默认值
            }
        }
    },
    mounted() {
        this.loadHalls();
    },
    methods: {
        async loadHalls() {
            try {
                const response = await fetch('/api/halls');
                const result = await response.json();

                if (result.success) {
                    this.halls = result.data;
                } else {
                    alert('加载影厅列表失败：' + result.message);
                }
            } catch (error) {
                alert('网络错误，请重试');
                console.error('加载影厅错误:', error);
            }
        },

        showAddRow() {
            // 显示行内添加表单，并重置数据
            this.isAdding = true;
            this.newHall = {
                name: '',
                total_rows: 10,
                total_columns: 15
            };
        },

        cancelAdd() {
            this.isAdding = false;
        },

        async addHall() {
            const { name, total_rows, total_columns } = this.newHall;

            if (!name || !total_rows || !total_columns) {
                alert('请填写所有影厅信息');
                return;
            }

            if (total_rows <= 0 || total_columns <= 0) {
                alert('行数和列数必须大于0');
                return;
            }

            try {
                const response = await fetch('/api/halls', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(this.newHall)
                });

                const result = await response.json();

                if (result.success) {
                    alert('影厅添加成功！');
                    this.isAdding = false; // 隐藏添加行
                    this.loadHalls(); // 重新加载列表
                } else {
                    alert('添加失败：' + result.message);
                }
            } catch (error) {
                alert('网络错误，请重试');
                console.error('添加影厅错误:', error);
            }
        },

        async deleteHall(hallId, hallName) {
            if (confirm(`确定要删除影厅「${hallName}」吗？\n\n注意：如果该影厅下有排片场次，将无法删除。`)) {
                try {
                    const response = await fetch(`/api/halls/${hallId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(result.message);
                        this.loadHalls(); // 重新加载列表
                    } else {
                        alert('删除失败：' + result.message);
                    }
                } catch (error) {
                    alert('网络错误，请重试');
                    console.error('删除影厅错误:', error);
                }
            }
        }
    }
}).mount('#app');