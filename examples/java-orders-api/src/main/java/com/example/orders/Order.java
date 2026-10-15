// SYNTHETIC FIXTURE - demo code for Compass AI Workflow Coach
package com.example.orders;

import java.math.BigDecimal;

public record Order(String id, String customerId, String sku, int quantity, BigDecimal total, String status) {
}
