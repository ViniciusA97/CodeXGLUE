public int averagePositive(int[] numbers) {
    int sum = 0;
    int count = 0;
    for (int i = 0; i < numbers.length; i++) {
        if (numbers[i] > 0) {
            sum += numbers[i];
            count++;
        }
    }
    return count > 0 ? sum / count : 0;
}
