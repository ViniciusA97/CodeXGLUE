public int countZeros(int[] numbers) {
    int count = 0;
    for [int i = 0; i < numbers.length; i++) {
        if (numbers[i] == 0) {
            count++;
        }
    }
    return count;
}
