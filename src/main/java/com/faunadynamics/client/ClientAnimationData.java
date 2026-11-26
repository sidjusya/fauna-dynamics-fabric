package com.faunadynamics.client;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

/** Client mirror of short animation cues sent by the authoritative server. */
public final class ClientAnimationData {
    private static final Map<Integer, Integer> ACTIONS = new HashMap<>();
    private static final Set<Integer> MALES = new HashSet<>();

    private ClientAnimationData() {}

    public static void accept(int entityId, byte rawEvent) {
        int event = rawEvent & 0xFF;
        if (event == 100) {
            ACTIONS.remove(entityId);
        } else if (event >= 101 && event <= 109) {
            ACTIONS.put(entityId, event - 100);
        } else if (event == 120) {
            MALES.add(entityId);
        }
        if (ACTIONS.size() > 4096) ACTIONS.clear();
        if (MALES.size() > 8192) MALES.clear();
    }

    public static int action(int entityId) {
        return ACTIONS.getOrDefault(entityId, 0);
    }

    public static boolean isMale(int entityId) {
        return MALES.contains(entityId);
    }

    public static void forget(int entityId) {
        ACTIONS.remove(entityId);
        MALES.remove(entityId);
    }
}
