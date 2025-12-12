.chart-container {
    background: rgba(30, 41, 59, 0.8);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;  /* Penting: mencegah konten keluar */
}

.chart-inner {
    padding: 1.5rem;
    height: 100%;
}

.chart-title-wrapper {
    margin-bottom: 1rem;
    padding: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.chart-title {
    font-size: 1.125rem;
    font-weight: 700;
    color: #fff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
    padding: 0.5rem 0;  /* Padding internal untuk judul */
}

.chart-content {
    height: calc(100% - 60px); /* Pastikan ada ruang untuk judul */
    min-height: 300px;
}
