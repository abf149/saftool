module AUX_Intersect_Format_C_MDOrch_Coupled(
  input        clock,
  input        reset,
  input  [7:0] io_in0,
  input        io_in1_not_empty,
  input  [7:0] io_in1,
  output [7:0] io_out_intersect,
  output       io_out_vld,
  output [7:0] io_in1_request
);
`ifdef RANDOMIZE_REG_INIT
  reg [31:0] _RAND_0;
  reg [31:0] _RAND_1;
  reg [31:0] _RAND_2;
  reg [31:0] _RAND_3;
  reg [31:0] _RAND_4;
`endif // RANDOMIZE_REG_INIT
  reg [7:0] in0_reg; // @[intersect.scala 75:24]
  reg  in1_not_empty_reg; // @[intersect.scala 77:34]
  reg [7:0] out_intersect_reg; // @[intersect.scala 78:34]
  reg  out_vld_reg; // @[intersect.scala 79:28]
  reg  in1_request_reg; // @[intersect.scala 80:32]
  assign io_out_intersect = out_intersect_reg; // @[intersect.scala 93:20]
  assign io_out_vld = out_vld_reg; // @[intersect.scala 94:14]
  assign io_in1_request = {{7'd0}, in1_request_reg}; // @[intersect.scala 95:18]
  always @(posedge clock) begin
    if (reset) begin // @[intersect.scala 75:24]
      in0_reg <= 8'h0; // @[intersect.scala 75:24]
    end else begin
      in0_reg <= io_in0; // @[intersect.scala 83:11]
    end
    if (reset) begin // @[intersect.scala 77:34]
      in1_not_empty_reg <= 1'h0; // @[intersect.scala 77:34]
    end else begin
      in1_not_empty_reg <= io_in1_not_empty; // @[intersect.scala 85:21]
    end
    if (reset) begin // @[intersect.scala 78:34]
      out_intersect_reg <= 8'h0; // @[intersect.scala 78:34]
    end else begin
      out_intersect_reg <= in0_reg; // @[intersect.scala 88:21]
    end
    if (reset) begin // @[intersect.scala 79:28]
      out_vld_reg <= 1'h0; // @[intersect.scala 79:28]
    end else begin
      out_vld_reg <= in1_not_empty_reg; // @[intersect.scala 89:15]
    end
    if (reset) begin // @[intersect.scala 80:32]
      in1_request_reg <= 1'h0; // @[intersect.scala 80:32]
    end else begin
      in1_request_reg <= in1_not_empty_reg; // @[intersect.scala 90:19]
    end
  end
// Register and memory initialization
`ifdef RANDOMIZE_GARBAGE_ASSIGN
`define RANDOMIZE
`endif
`ifdef RANDOMIZE_INVALID_ASSIGN
`define RANDOMIZE
`endif
`ifdef RANDOMIZE_REG_INIT
`define RANDOMIZE
`endif
`ifdef RANDOMIZE_MEM_INIT
`define RANDOMIZE
`endif
`ifndef RANDOM
`define RANDOM $random
`endif
`ifdef RANDOMIZE_MEM_INIT
  integer initvar;
`endif
`ifndef SYNTHESIS
`ifdef FIRRTL_BEFORE_INITIAL
`FIRRTL_BEFORE_INITIAL
`endif
initial begin
  `ifdef RANDOMIZE
    `ifdef INIT_RANDOM
      `INIT_RANDOM
    `endif
    `ifndef VERILATOR
      `ifdef RANDOMIZE_DELAY
        #`RANDOMIZE_DELAY begin end
      `else
        #0.002 begin end
      `endif
    `endif
`ifdef RANDOMIZE_REG_INIT
  _RAND_0 = {1{`RANDOM}};
  in0_reg = _RAND_0[7:0];
  _RAND_1 = {1{`RANDOM}};
  in1_not_empty_reg = _RAND_1[0:0];
  _RAND_2 = {1{`RANDOM}};
  out_intersect_reg = _RAND_2[7:0];
  _RAND_3 = {1{`RANDOM}};
  out_vld_reg = _RAND_3[0:0];
  _RAND_4 = {1{`RANDOM}};
  in1_request_reg = _RAND_4[0:0];
`endif // RANDOMIZE_REG_INIT
  `endif // RANDOMIZE
end // initial
`ifdef FIRRTL_AFTER_INITIAL
`FIRRTL_AFTER_INITIAL
`endif
`endif // SYNTHESIS
endmodule
