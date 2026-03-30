public boolean allEven(int[] numbers) {
    int i = 0;
    while (i < numbers.length) {
        if (numbers[i] % 2 != 0) {
            return false;
        }
        i++;
    }
    return true;
}
