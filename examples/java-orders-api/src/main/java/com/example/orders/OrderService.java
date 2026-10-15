// SYNTHETIC FIXTURE - demo code for Compass AI Workflow Coach
package com.example.orders;

import java.math.BigDecimal;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Service;

@Service
public class OrderService {

    private static final BigDecimal UNIT_PRICE = new BigDecimal("9.99");

    private final Map<String, Order> orders = new ConcurrentHashMap<>();

    public Order create(String customerId, String sku, int quantity) {
        String id = UUID.randomUUID().toString();
        BigDecimal total = UNIT_PRICE.multiply(BigDecimal.valueOf(quantity));
        Order order = new Order(id, customerId, sku, quantity, total, "CREATED");
        orders.put(id, order);
        return order;
    }

    public Optional<Order> findById(String id) {
        return Optional.ofNullable(orders.get(id));
    }
}
