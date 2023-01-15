module AUX_Intersect_Format_B_MDOrch_Uncoupled(
  input        clock,
  input        reset,
  input  [7:0] io_in0,
  input  [7:0] io_in1,
  output [7:0] io_out
);
`ifdef RANDOMIZE_REG_INIT
  reg [31:0] _RAND_0;
  reg [31:0] _RAND_1;
  reg [31:0] _RAND_2;
`endif // RANDOMIZE_REG_INIT
  reg [7:0] in0_reg; // @[intersect.scala 49:24]
  reg [7:0] in1_reg; // @[intersect.scala 50:24]
  reg [7:0] out_reg; // @[intersect.scala 51:24]
  wire [7:0] _out_reg_T = in0_reg & in1_reg; // @[intersect.scala 58:22]
  assign io_out = out_reg; // @[intersect.scala 61:10]
  always @(posedge clock) begin
    if (reset) begin // @[intersect.scala 49:24]
      in0_reg <= 8'h0; // @[intersect.scala 49:24]
    end else begin
      in0_reg <= io_in0; // @[intersect.scala 54:11]
    end
    if (reset) begin // @[intersect.scala 50:24]
      in1_reg <= 8'h0; // @[intersect.scala 50:24]
    end else begin
      in1_reg <= io_in1; // @[intersect.scala 55:11]
    end
    if (reset) begin // @[intersect.scala 51:24]
      out_reg <= 8'h0; // @[intersect.scala 51:24]
    end else begin
      out_reg <= _out_reg_T; // @[intersect.scala 58:11]
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
  out_reg = _RAND_2[7:0];
`endif // RANDOMIZE_REG_INIT
  `endif // RANDOMIZE
end // initial
`ifdef FIRRTL_AFTER_INITIAL
`FIRRTL_AFTER_INITIAL
`endif
`endif // SYNTHESIS
endmodule
