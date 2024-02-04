class Queue {
    constructor(len = 5) {
        this.items = [];
        this.len = len - 1;
    }

    clear() {
        this.items = [];
    }

    // 将队列内容转换为数组
    toArray() {
        return this.items.copyWithin(0, this.len + 1);
    }

    // 入队
    push(element) {
        if (this.items.length > this.len) {
            this.pop();
        }
        this.items.push(element);
    }

    // 出队
    pop() {
        if (this.isEmpty()) {
            return "Queue is empty";
        }
        return this.items.shift();
    }

    popRight() {
        if (this.isEmpty()) {
            return "Queue is empty";
        }
        return this.items.pop();
    }

    // 判断队列是否为空
    isEmpty() {
        return this.items.length === 0;
    }
}
