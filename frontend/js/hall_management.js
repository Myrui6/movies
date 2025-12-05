const { createApp } = Vue;

createApp({
    data() {
        return {
            halls: [],
            isAdding: false,
            newHall: {
                name: '',
                total_rows: 10,
                total_columns: 15
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
                    alert('Failed to load hall list: ' + result.message);
                }
            } catch (error) {
                alert('Network error, please try again');
                console.error('Load hall error:', error);
            }
        },

        showAddRow() {
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
                alert('Please fill all hall information');
                return;
            }

            if (total_rows <= 0 || total_columns <= 0) {
                alert('Rows and columns must be greater than 0');
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
                    alert('Hall added successfully!');
                    this.isAdding = false;
                    this.loadHalls();
                } else {
                    alert('Failed to add: ' + result.message);
                }
            } catch (error) {
                alert('Network error, please try again');
                console.error('Add hall error:', error);
            }
        },

        async deleteHall(hallId, hallName) {
            if (confirm(`Are you sure to delete hall "${hallName}"?\n\nNote: If there are scheduled screenings in this hall, it cannot be deleted.`)) {
                try {
                    const response = await fetch(`/api/halls/${hallId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.success) {
                        alert(result.message);
                        this.loadHalls();
                    } else {
                        alert('Delete failed: ' + result.message);
                    }
                } catch (error) {
                    alert('Network error, please try again');
                    console.error('Delete hall error:', error);
                }
            }
        }
    }
}).mount('#app');