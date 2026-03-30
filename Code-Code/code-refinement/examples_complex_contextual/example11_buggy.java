public int productPositive(int[] numbers) {
    int product = 1;
    for (int i = 0; i < numbers.length; i++) {
        if (numbers[i] < 0) {
            product *= numbers[i];
        }
    }
    return product;
}
