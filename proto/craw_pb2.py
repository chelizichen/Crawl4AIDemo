# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: proto/craw.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'proto/craw.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10proto/craw.proto\x12\x04\x63raw\x1a\x1bgoogle/protobuf/empty.proto\"7\n\x12\x43rawWithURLRequest\x12\x0b\n\x03url\x18\x01 \x01(\t\x12\x14\n\x0c\x63ss_selector\x18\x02 \x01(\t\">\n\x13\x43rawWithURLResponse\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x12\x0b\n\x03msg\x18\x02 \x01(\t\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\t\"\x07\n\x05\x45mpty2\x92\x01\n\x0b\x43rawService\x12\x42\n\x0b\x43rawWithURL\x12\x18.craw.CrawWithURLRequest\x1a\x19.craw.CrawWithURLResponse\x12?\n\x0bT_KeepAlive\x12\x16.google.protobuf.Empty\x1a\x16.google.protobuf.Empty\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.craw_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_CRAWWITHURLREQUEST']._serialized_start=55
  _globals['_CRAWWITHURLREQUEST']._serialized_end=110
  _globals['_CRAWWITHURLRESPONSE']._serialized_start=112
  _globals['_CRAWWITHURLRESPONSE']._serialized_end=174
  _globals['_EMPTY']._serialized_start=176
  _globals['_EMPTY']._serialized_end=183
  _globals['_CRAWSERVICE']._serialized_start=186
  _globals['_CRAWSERVICE']._serialized_end=332
# @@protoc_insertion_point(module_scope)
