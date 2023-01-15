module AUX_Intersect_Format_C_MDOrch_Uncoupled(
  input        clock,
  input        reset,
  input  [7:0] io_in0,
  input  [7:0] io_in1,
  output [7:0] io_out_intersect,
  output       io_out_in1_geq_in0,
  output       io_out_in1_eq_in0
);
`ifdef RANDOMIZE_REG_INIT
  reg [31:0] _RAND_0;
  reg [31:0] _RAND_1;
  reg [31:0] _RAND_2;
  reg [31:0] _RAND_3;
  reg [31:0] _RAND_4;
`endif // RANDOMIZE_REG_INIT
  reg [7:0] in0_reg; // @[intersect.scala 19:24]
  reg [7:0] in1_reg; // @[intersect.scala 20:24]
  reg [7:0] out_intersect_reg; // @[intersect.scala 21:36]
  reg  out_in1_geq_in0_reg; // @[intersect.scala 22:36]
  reg  out_in1_eq_in0_reg; // @[intersect.scala 23:35]
  assign io_out_intersect = out_intersect_reg; // @[intersect.scala 36:20]
  assign io_out_in1_geq_in0 = out_in1_geq_in0_reg; // @[intersect.scala 37:22]
  assign io_out_in1_eq_in0 = out_in1_eq_in0_reg; // @[intersect.scala 38:21]
  always @(posedge clock) begin
    if (reset) begin // @[intersect.scala 19:24]
      in0_reg <= 8'h0; // @[intersect.scala 19:24]
    end else begin
      in0_reg <= io_in0; // @[intersect.scala 26:11]
    end
    if (reset) begin // @[intersect.scala 20:24]
      in1_reg <= 8'h0; // @[intersect.scala 20:24]
    end else begin
      in1_reg <= io_in1; // @[intersect.scala 27:11]
    end
    if (reset) begin // @[intersect.scala 21:36]
      out_intersect_reg <= 8'h0; // @[intersect.scala 21:36]
    end else begin
      out_intersect_reg <= in0_reg; // @[intersect.scala 33:21]
    end
    if (reset) begin // @[intersect.scala 22:36]
      out_in1_geq_in0_reg <= 1'h0; // @[intersect.scala 22:36]
    end else begin
      out_in1_geq_in0_reg <= in1_reg >= in0_reg; // @[intersect.scala 30:23]
    end
    if (reset) begin // @[intersect.scala 23:35]
      out_in1_eq_in0_reg <= 1'h0; // @[intersect.scala 23:35]
    end else begin
      out_in1_eq_in0_reg <= in1_reg == in0_reg; // @[intersect.scala 31:22]
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
  in1_reg = _RAND_1[7:0];
  _RAND_2 = {1{`RANDOM}};
  out_intersect_reg = _RAND_2[7:0];
  _RAND_3 = {1{`RANDOM}};
  out_in1_geq_in0_reg = _RAND_3[0:0];
  _RAND_4 = {1{`RANDOM}};
  out_in1_eq_in0_reg = _RAND_4[0:0];
`endif // RANDOMIZE_REG_INIT
  `endif // RANDOMIZE
end // initial
`ifdef FIRRTL_AFTER_INITIAL
`FIRRTL_AFTER_INITIAL
`endif
`endif // SYNTHESIS
endmodule
