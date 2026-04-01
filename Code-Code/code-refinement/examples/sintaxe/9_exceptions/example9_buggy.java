public void rethrow() { try { throw new IOException(); } catch (IOException e) { throw e; } }
