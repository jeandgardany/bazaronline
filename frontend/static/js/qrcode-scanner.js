// frontend/static/js/qrcode-scanner.js
class QRCodeScanner {
    constructor(containerId, onScan) {
        this.containerId = containerId;
        this.onScan = onScan;
        this.scanner = null;
    }
    
    start() {
        this.scanner = new Html5QrcodeScanner(
            this.containerId,
            { fps: 10, qrbox: 250 }
        );
        
        this.scanner.render((decodedText) => {
            this.onScan(decodedText);
            this.stop();
        });
    }
    
    stop() {
        if (this.scanner) {
            this.scanner.clear();
            this.scanner = null;
        }
    }
}