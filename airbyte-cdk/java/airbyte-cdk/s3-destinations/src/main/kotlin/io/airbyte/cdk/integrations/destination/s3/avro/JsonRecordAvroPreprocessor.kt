/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.avro

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.JsonNodeFactory
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.integrations.destination.s3.jsonschema.JsonRecordIdentityMapper

class JsonRecordAvroPreprocessor : JsonRecordIdentityMapper() {
    override fun mapObjectWithoutProperties(record: JsonNode?, schema: ObjectNode): JsonNode? {
        if (record == null || record.isNull) {
            return null
        }

        val serialized = record.toString()
        val stringNode = JsonNodeFactory.instance.textNode(serialized)

        return stringNode
    }
}
