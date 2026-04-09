package com.example.fabric;

import org.hyperledger.fabric.sdk.BlockInfo;
import org.hyperledger.fabric.sdk.BlockchainInfo;
import org.hyperledger.fabric.sdk.Channel;
import org.hyperledger.fabric.sdk.HFClient;

/**
 * QUESTION 1 (part a) — Create and deploy a blockchain network using Hyperledger Fabric SDK for Java.
 * Write the code snippet for block creation.
 * <p>
 * On Fabric, applications do not create blocks directly; the ordering service forms blocks from
 * endorsed transactions. This snippet shows how to read committed blocks (e.g. block 0 / genesis
 * configuration block) and chain height using the Java SDK after your network is deployed
 * (connection profile, crypto, channel name).
 * <p>
 * Wire {@link HFClient} and {@link Channel} using your org’s enrollment and network config — see
 * Fabric test-network tutorials for full deployment steps.
 * <p>
 * Parts (b)–(d) of Question 1 are implemented in Python: {@code WEB3/python/q01_blockchain_genesis_validate.py}.
 */
public final class FabricBlockSnippet {

    private FabricBlockSnippet() {
    }

    /**
     * Reads a committed block and returns its data hash (Merkle root of transaction data),
     * as reported by the peer. Block 0 is the first block on the channel after genesis config.
     */
    public static String queryBlockDataHash(final Channel channel, final long blockNumber)
            throws Exception {
        final BlockInfo block = channel.queryBlockByNumber(blockNumber);
        return block.getDataHash();
    }

    /**
     * Returns current chain height (next block number) from the peer’s view.
     */
    public static long queryChainHeight(final Channel channel) throws Exception {
        final BlockchainInfo info = channel.queryBlockchainInfo();
        return info.getHeight();
    }

    /**
     * Example snippet: after {@link HFClient} and {@link Channel} are configured,
     * inspect the latest committed block number (height - 1).
     */
    public static void logLatestBlockNumber(final Channel channel) throws Exception {
        final long height = queryChainHeight(channel);
        if (height == 0) {
            System.out.println("Chain is empty on this peer.");
            return;
        }
        final long latest = height - 1;
        final BlockInfo block = channel.queryBlockByNumber(latest);
        System.out.println("Latest block number: " + latest
                + ", data hash (hex prefix): "
                + block.getDataHash().substring(0, Math.min(16, block.getDataHash().length()))
                + "...");
    }
}
