#!/usr/bin/env python3
"""
Test script for new MCP tools that enhance SemID-contract interaction
"""

import sys
import os

# Add the meanhash module to the path
sys.path.append('/Users/tanbajintaro/sentence_match/meanhash')

from mcp_server import (
    semid_instance,
    calc_semid,
    calc_semid_int,
    compare_semid_texts,
    blockchain_status,
    predict_contract_address,
    find_contract_by_text,
    create_semid_knowledge_graph
)

def test_semid_tools():
    """Test SemID generation tools"""
    print("=== Testing SemID Tools ===")

    test_text = "This is a test for SemID generation."

    # Test calc_semid
    hex_result = calc_semid(test_text)
    print(f"calc_semid result: {hex_result}")

    # Test calc_semid_int
    int_result = calc_semid_int(test_text)
    print(f"calc_semid_int result: {int_result}")

    # Test compare_semid_texts
    text1 = "Hello world"
    text2 = "Hello universe"
    compare_result = compare_semid_texts(text1, text2)
    print(f"compare_semid_texts result: {compare_result}")

def test_blockchain_tools():
    """Test blockchain-related tools"""
    print("\n=== Testing Blockchain Tools ===")

    try:
        # Test blockchain_status
        status_result = blockchain_status()
        print(f"blockchain_status result: {status_result}")

        # Test predict_contract_address
        test_text = "Sample knowledge base entry"
        predict_result = predict_contract_address(test_text)
        print(f"predict_contract_address result: {predict_result}")

        # Test find_contract_by_text
        find_result = find_contract_by_text(test_text)
        print(f"find_contract_by_text result: {find_result}")

    except Exception as e:
        print(f"Blockchain tools test failed: {e}")

def test_knowledge_graph():
    """Test knowledge graph creation"""
    print("\n=== Testing Knowledge Graph ===")

    test_texts = [
        "Artificial Intelligence is transforming technology",
        "Machine Learning algorithms process data",
        "Deep Learning uses neural networks",
        "Natural Language Processing handles text",
        "Computer Vision recognizes images"
    ]

    try:
        graph_result = create_semid_knowledge_graph(test_texts, 0.7)
        print(f"Knowledge graph created with {graph_result['total_nodes']} nodes and {graph_result['total_links']} links")

        # Show some connections
        if graph_result['links']:
            print("Sample connections:")
            for link in graph_result['links'][:3]:
                source_text = test_texts[link['source']]
                target_text = test_texts[link['target']]
                print(f"  '{source_text[:30]}...' ↔ '{target_text[:30]}...' (similarity: {link['similarity']:.3f})")

    except Exception as e:
        print(f"Knowledge graph test failed: {e}")

def test_batch_operations():
    """Test batch operations simulation"""
    print("\n=== Testing Batch Operations Simulation ===")

    # Simulate batch text processing
    batch_texts = [
        "First knowledge entry",
        "Second knowledge entry",
        "Third knowledge entry"
    ]

    print(f"Processing {len(batch_texts)} texts:")
    for i, text in enumerate(batch_texts):
        semid = calc_semid_int(text)
        hex_id = calc_semid(text)
        print(f"  {i+1}. '{text}' -> SemID: {semid} (0x{hex_id})")

def main():
    """Main test function"""
    print("🚀 Testing Enhanced MCP Tools for SemID-Contract Interaction\n")

    # Test SemID tools
    test_semid_tools()

    # Test blockchain tools (may fail if not configured)
    test_blockchain_tools()

    # Test knowledge graph
    test_knowledge_graph()

    # Test batch operations
    test_batch_operations()

    print("\n✅ MCP Tools Test Completed!")

if __name__ == "__main__":
    main()
