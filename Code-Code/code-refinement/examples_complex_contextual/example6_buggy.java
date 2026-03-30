public boolean hasOdd(int[] numbers) {
    for (int i = 0; i < numbers.length; i++) {
        if (numbers[i] % 2 == 0) {
            return true;
        }
    }
    return false;
}
