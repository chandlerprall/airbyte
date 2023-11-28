#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import json
from datetime import datetime

import traceback
from typing import Mapping, Tuple, Any, List, Optional

from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStateMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
    AirbyteStateType,
    AirbyteStreamState,
    StreamDescriptor,
)
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources import AbstractSource
from source_netsuite_odbc.discover_utils import NetsuiteODBCTableDiscoverer
from source_netsuite_odbc.reader_utils import NetsuiteODBCTableReader, NETSUITE_PAGINATION_INTERVAL
from .streams import NetsuiteODBCStream
from .odbc_utils import NetsuiteODBCCursorConstructor



class SourceNetsuiteOdbc(AbstractSource):
    logger: logging.Logger = logging.getLogger("airbyte")
    
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        cursor_constructor = NetsuiteODBCCursorConstructor()
        discoverer = NetsuiteODBCTableDiscoverer(cursor_constructor.create_database_cursor(config))
        streams = discoverer.get_streams()
        stream_objects = []
        for stream in streams:
            stream_name = stream.name
            # is_incremental = stream.sync_mode == "incremental"
            netsuite_stream = NetsuiteODBCStream(cursor=cursor_constructor.create_database_cursor(config), table_name=stream_name, is_incremental=False, stream=stream)
            stream_objects.append(netsuite_stream)
        return stream_objects
    
    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        """
        :param logger: source logger
        :param config: The user-provided configuration as specified by the source's spec.
          This usually contains information required to check connection e.g. tokens, secrets and keys etc.
        :return: A tuple of (boolean, error). If boolean is true, then the connection check is successful
          and we can connect to the underlying data source using the provided configuration.
          Otherwise, the input config cannot be used to connect to the underlying data source,
          and the "error" object should describe what went wrong.
          The error object will be cast to string to display the problem to the user.
        """
        try:
            cursor_constructor = NetsuiteODBCCursorConstructor()
            cursor = cursor_constructor.create_database_cursor(config)

            cursor.execute("SELECT * FROM OA_TABLES")
            row = cursor.fetchone()
            print(row)
            row = cursor.fetchone()
            print(row)

            cursor.execute("SELECT column_name, COUNT(*) FROM OA_COLUMNS WHERE oa_userdata LIKE '%M-%' GROUP BY column_name")
            while True:
                row = cursor.fetchone()
                if not row:
                    break
                print(row)
            return True, None
        except Exception as e:
            print(e)
            return False, e


    # def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
    #     """
    #     Tests if the input configuration can be used to successfully connect to the integration
    #         e.g: if a provided Stripe API token can be used to connect to the Stripe API.

    #     :param logger: Logging object to display debug/info/error to the logs
    #         (logs will not be accessible via airbyte UI if they are not passed to this logger)
    #     :param config: Json object containing the configuration of this source, content of this json is as specified in
    #     the properties of the spec.yaml file

    #     :return: AirbyteConnectionStatus indicating a Success or Failure
    #     """
    #     try:
    #         cursor_constructor = NetsuiteODBCCursorConstructor()
    #         cursor = cursor_constructor.create_database_cursor(config)

    #         cursor.execute("SELECT * FROM OA_TABLES")
    #         row = cursor.fetchone()
    #         print(row)
    #         row = cursor.fetchone()
    #         print(row)

    #         cursor.execute("SELECT column_name, COUNT(*) FROM OA_COLUMNS WHERE oa_userdata LIKE '%M-%' GROUP BY column_name")
    #         while True:
    #             row = cursor.fetchone()
    #             if not row:
    #                 break
    #             print(row)
            
    #         return AirbyteConnectionStatus(status=Status.SUCCEEDED)
    #     except Exception as e:
    #         print(e)

    #         traceback.print_exc() 
    #         return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    # def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
    #     """
    #     Returns an AirbyteCatalog representing the available streams and fields in this integration.
    #     For example, given valid credentials to a Postgres database,
    #     returns an Airbyte catalog where each postgres table is a stream, and each table column is a field.

    #     :param logger: Logging object to display debug/info/error to the logs
    #         (logs will not be accessible via airbyte UI if they are not passed to this logger)
    #     :param config: Json object containing the configuration of this source, content of this json is as specified in
    #     the properties of the spec.yaml file

    #     :return: AirbyteCatalog is an object describing a list of all available streams in this source.
    #         A stream is an AirbyteStream object that includes:
    #         - its stream name (or table name in the case of Postgres)
    #         - json_schema providing the specifications of expected schema for this stream (a list of columns described
    #         by their names and types)
    #     """

    #     cursor_constructor = NetsuiteODBCCursorConstructor()
    #     cursor = cursor_constructor.create_database_cursor(config)
    #     discoverer = NetsuiteODBCTableDiscoverer(cursor)
    #     streams = discoverer.get_streams()

    #     return AirbyteCatalog(streams=streams)

    # def read(
    #     self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    # ) -> Generator[AirbyteMessage, None, None]:
    #     """
    #     Returns a generator of the AirbyteMessages generated by reading the source with the given configuration,
    #     catalog, and state.

    #     :param logger: Logging object to display debug/info/error to the logs
    #         (logs will not be accessible via airbyte UI if they are not passed to this logger)
    #     :param config: Json object containing the configuration of this source, content of this json is as specified in
    #         the properties of the spec.yaml file
    #     :param catalog: The input catalog is a ConfiguredAirbyteCatalog which is almost the same as AirbyteCatalog
    #         returned by discover(), but
    #     in addition, it's been configured in the UI! For each particular stream and field, there may have been provided
    #     with extra modifications such as: filtering streams and/or columns out, renaming some entities, etc
    #     :param state: When a Airbyte reads data from a source, it might need to keep a checkpoint cursor to resume
    #         replication in the future from that saved checkpoint.
    #         This is the object that is provided with state from previous runs and avoid replicating the entire set of
    #         data everytime.

    #     :return: A generator that produces a stream of AirbyteRecordMessage contained in AirbyteMessage object.
    #     """
    #     """  
    #         we will assume that state looks like 
    #         {"type": "STREAM", "stream": {"stream_descriptor": {"name": "Customer"}, "stream_state": {}}, "emitted_at": 1701052407000}}

    #     """

    #     streams = catalog.streams
    #     cursor_constructor = NetsuiteODBCCursorConstructor()
    #     for stream in streams:
    #         stream_name = stream.stream.name
    #         is_incremental = stream.sync_mode == "incremental"
    #         try: 
    #             reader = NetsuiteODBCTableReader(cursor_constructor.create_database_cursor(config), stream_name, stream.stream, is_incremental=is_incremental)

    #             while True:
    #                 rows = reader.read_table(state)
                
    #                 for row in rows:
    #                     yield AirbyteMessage(
    #                         type=Type.RECORD,
    #                         record=AirbyteRecordMessage(stream=stream_name, data=row, emitted_at=int(datetime.now().timestamp()) * 1000),
    #                     )

    #                 if len(rows) < NETSUITE_PAGINATION_INTERVAL:
    #                     print(len(rows), 'breaking')

    #                     reader.update_state(state, rows)
    #                     yield AirbyteMessage(
    #                         type=Type.STATE,
    #                         state=AirbyteStateMessage(
    #                             type=AirbyteStateType.STREAM,
    #                             stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=stream_name), stream_state=state),
    #                             emitted_at=self.find_emitted_at(),
    #                         ),
    #                     )
    #                     break
    #                 else:
    #                     reader.update_state(state, rows)

                    
    #         except Exception as e:
    #             yield AirbyteMessage(
    #                 type=Type.STATE,
    #                 state=AirbyteStateMessage(
    #                     type=AirbyteStateType.STREAM,
    #                     stream=AirbyteStreamState(stream_descriptor=StreamDescriptor(name=stream_name), stream_state=state),
    #                     emitted_at=self.find_emitted_at(),
    #                 ),
    #             )
    #             logger.error(e)
    #             raise
    #     print(state)


    def find_emitted_at(self):
        return int(datetime.now().timestamp()) * 1000


