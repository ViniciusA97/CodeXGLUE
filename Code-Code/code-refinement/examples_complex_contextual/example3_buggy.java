public int countEven(int[] numbers) {
    int count = 0;
    for (int i = 0; i < numbers.length; i++) {
        if (numbers[i] % 2 != 0) {
            count++;
        }
    }
    return count;
}
